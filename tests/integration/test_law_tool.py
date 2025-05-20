from src.laws.db import LawDatabase
from src.tools.law import law_lookup


def test_law_ingestion_and_lookup(tmp_path):
    db_path = tmp_path / "laws.db"
    db = LawDatabase(str(db_path))
    db.ingest_zip_file("xml.zip")

    result = law_lookup("§ 1a", "UStG", db_path=str(db_path))
    assert isinstance(result, dict)
    assert "Innergemeinschaftlicher Erwerb" in result["title"]
    assert len(result["text"]) > 0

