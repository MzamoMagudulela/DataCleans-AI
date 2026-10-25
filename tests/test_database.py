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
    assert audits[0]["initial_health_score"] == 85.5


def test_log_cleaning_step_and_update(test_db):
    audit_id = test_db.log_dataset_upload("test.csv", 50, 4, 90.0)
    step_id = test_db.log_cleaning_step(
        audit_id=audit_id,
        step_number=1,
        operation_name="Drop Duplicates",
        affected_rows=5,
    )
    assert step_id is not None
    assert step_id > 0

    # Retrieve steps
    steps = test_db.get_audit_steps(audit_id)
    assert len(steps) == 1
    assert steps[0]["operation_name"] == "Drop Duplicates"
    assert steps[0]["affected_rows"] == 5

    # Update completion
    test_db.update_audit_completion(audit_id, final_rows=45, final_columns=4, final_health_score=98.0)
    updated_audits = test_db.get_recent_audits()
    assert updated_audits[0]["final_rows"] == 45
    assert updated_audits[0]["final_health_score"] == 98.0
    assert updated_audits[0]["status"] == "Cleaned"
