from __future__ import annotations

"""Utility classes for storing and querying law texts."""

import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, create_engine, select
from sqlalchemy.orm import Session, declarative_base


Base = declarative_base()


class LawSection(Base):
    __tablename__ = "law_sections"

    id = Column(Integer, primary_key=True)
    abbreviation = Column(String, index=True)
    doc_number = Column(String, index=True)
    section = Column(String, index=True)
    title = Column(String)
    text = Column(Text)


@dataclass
class LawDatabase:
    """Simple SQLite-backed database for German laws."""

    db_path: str = "laws.db"

    def __post_init__(self) -> None:
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)

    def ingest_zip_url(self, url: str) -> None:
        """Download a zip file containing an XML law document and ingest it."""
        import requests

        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = os.path.join(tmp, "law.zip")
            with open(zip_path, "wb") as f:
                f.write(response.content)
            self.ingest_zip_file(zip_path)

    def ingest_zip_file(self, zip_path: str) -> None:
        """Ingest a local xml.zip archive."""
        with zipfile.ZipFile(zip_path) as zf:
            xml_name = next((n for n in zf.namelist() if n.endswith(".xml")), None)
            if not xml_name:
                raise ValueError("No XML file found in archive")
            with zf.open(xml_name) as f:
                self.ingest_xml_bytes(f.read())

    def ingest_xml_bytes(self, data: bytes) -> None:
        root = ET.fromstring(data)
        with Session(self.engine) as session:
            for norm in root.findall("norm"):
                meta = norm.find("metadaten")
                if meta is None:
                    continue
                section = meta.findtext("enbez")
                if not section:
                    continue
                title = meta.findtext("titel", default="")
                jbs = [j.text for j in meta.findall("jurabk") if j.text]
                abbreviation = jbs[-1] if jbs else None
                doc_number = norm.get("doknr") or ""
                text_elem = norm.find("textdaten/text")
                text = ""
                if text_elem is not None:
                    text = "".join(text_elem.itertext()).strip()
                session.add(
                    LawSection(
                        abbreviation=abbreviation,
                        doc_number=doc_number,
                        section=section,
                        title=title,
                        text=text,
                    )
                )
            session.commit()

    def query_section(
        self, abbreviation: str, section: str
    ) -> Optional[LawSection]:
        with Session(self.engine) as session:
            stmt = (
                select(LawSection)
                .where(LawSection.abbreviation == abbreviation)
                .where(LawSection.section == section)
            )
            return session.scalars(stmt).first()
