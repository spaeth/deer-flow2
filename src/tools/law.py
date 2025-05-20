from __future__ import annotations

"""Tool for retrieving law sections from the local database."""

import logging
from typing import Annotated

from langchain_core.tools import tool

from src.laws.db import LawDatabase
from .decorators import log_io

logger = logging.getLogger(__name__)


@tool
@log_io
def law_lookup(
    section: Annotated[str, "Section number like '§ 1a'"],
    abbreviation: Annotated[str, "Law abbreviation like 'UStG'"],
    db_path: str = "laws.db",
) -> dict[str, str] | str:
    """Lookup a law section by abbreviation and section number."""
    db = LawDatabase(db_path)
    result = db.query_section(abbreviation, section)
    if result is None:
        return f"Section {section} not found in {abbreviation}."
    return {"title": result.title, "text": result.text}
