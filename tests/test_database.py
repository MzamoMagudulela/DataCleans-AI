"""
Unit tests for DatabaseManager.
"""

import pytest
from src.database import DatabaseManager


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_datacleans.db"
    manager = DatabaseManager(f"sqlite:///{db_file.as_posix()}")
    manager.init_db()
    return manager


def test_init_and_log_session(test_db):
    audit_id = test_db.log_dataset_upload(
        dataset_name="test_data.csv",
        initial_rows=100,
        initial_columns=5,
        health_score=85.5,
    )
    assert audit_id is not None
    assert audit_id > 0

    audits = test_db.get_recent_audits()
    assert len(audits) == 1
    assert audits[0]["dataset_name"] == "test_data.csv"
    assert audits[0]["initial_rows"] == 100
    assert audits[0]["health_score"] == 85.5


def test_log_cleaning_step(test_db):
    audit_id = test_db.log_dataset_upload("test.csv", 50, 4, 90.0)
    step_id = test_db.log_cleaning_step(
        audit_id=audit_id,
        step_number=1,
        operation_name="Drop Duplicates",
        affected_rows=5,
    )
    assert step_id is not None
    assert step_id > 0
