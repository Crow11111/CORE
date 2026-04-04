from unittest.mock import MagicMock

import pytest
from typing import Dict, Any

from src.logic_core.arbitration_engine import (
    STATUS_BLOCKED_ON_EVIDENCE,
    STATUS_EFFERENCE_SUBMITTED,
    STATUS_PROCESSING,
    get_next_job,
    commit_job_result,
    check_liveness,
    evaluate_evidence,
    MergeConflictError,
    EntropicDeadlockError,
)


def test_priority_scheduler():
    """Trap 1: Priority Scheduler (A6)"""

    # Test A: Priority & Arrival (1 is High priority)
    queue = [
        {"job_id": "job_3", "priority": 2, "expected_arrival": 100.0, "status": "pending"},
        {"job_id": "job_1", "priority": 1, "expected_arrival": 150.0, "status": "pending"},
        {"job_id": "job_2", "priority": 1, "expected_arrival": 120.0, "status": "pending"},
    ]

    assigned = get_next_job(queue, 2)
    assert len(assigned) == 2
    # job_2 has priority 1 and arrival 120.0 (earliest among priority 1)
    assert assigned[0]["job_id"] == "job_2"
    # job_1 has priority 1 and arrival 150.0
    assert assigned[1]["job_id"] == "job_1"

    # Test B: Starvation Protection
    queue_with_running = [
        {"job_id": "job_run", "priority": 5, "expected_arrival": 50.0, "status": "processing"},
        {"job_id": "job_high", "priority": 1, "expected_arrival": 120.0, "status": "pending"},
    ]

    assigned = get_next_job(queue_with_running, 1)
    # The running job must NOT be replaced/aborted
    assert len(assigned) == 1
    assert assigned[0]["job_id"] == "job_run"

    # If 2 workers, both should run
    assigned = get_next_job(queue_with_running, 2)
    assert len(assigned) == 2
    assert assigned[0]["job_id"] == "job_run"
    assert assigned[1]["job_id"] == "job_high"


def test_single_job_merge_rule():
    """Trap 2: Single-Job Merge Rule (First-Wins & Jahn-Teller) — state + optional persist."""

    persist = MagicMock()

    job_alpha: Dict[str, Any] = {"job_id": "job_alpha", "status": "processing"}
    # Test A: First Commit
    success = commit_job_result(job_alpha, {"data": 42}, 0.95, persist=persist)
    assert success is True
    assert job_alpha["status"] == STATUS_EFFERENCE_SUBMITTED
    assert job_alpha["result"] == {"data": 42}
    persist.assert_called_once_with(job_alpha)
    persist.reset_mock()

    # Test B: Late Arriver (MergeConflictError) — same record, already committed
    with pytest.raises(MergeConflictError):
        commit_job_result(job_alpha, {"data": 43}, 0.95, persist=persist)
    persist.assert_not_called()
    assert job_alpha["result"] == {"data": 42}

    # Test C: Jahn-Teller-Symmetriebruch / Anti-0.5 (fresh jobs, no global set)
    for conf in (0.50, 0.49, 0.51):
        j: Dict[str, Any] = {"job_id": f"job_jt_{conf}", "status": "processing"}
        with pytest.raises(EntropicDeadlockError):
            commit_job_result(j, {"data": 1}, conf, persist=persist)
        assert j["status"] == "processing"
        assert "result" not in j


def test_liveness_monitor():
    """Trap 3: Liveness Monitor (Heartbeat)"""
    # check_liveness(job_id: str, last_heartbeat: float, current_time: float, timeout: float) -> str

    # Test A: Alive
    assert check_liveness("job_1", 100.0, 105.0, 10.0) == "processing"

    # Test B: Dead
    assert check_liveness("job_1", 100.0, 110.0, 10.0) == "failed"
    assert check_liveness("job_1", 100.0, 115.0, 10.0) == "failed"


def test_evaluate_evidence():
    """Trap 4: A10 Occam's Negative Razor — job status mutated + persist on blocked path."""

    persist = MagicMock()

    # Test A: Ausreichend Evidenz
    job_ok: Dict[str, Any] = {"job_id": "job_1", "status": "processing"}
    assert evaluate_evidence(job_ok, 5, 0.5, persist=persist) == STATUS_PROCESSING
    assert job_ok["status"] == STATUS_PROCESSING
    persist.assert_called_once_with(job_ok)
    persist.reset_mock()

    # Test B: Evidenz erschöpft
    job_b: Dict[str, Any] = {"job_id": "job_1", "status": "processing"}
    assert evaluate_evidence(job_b, 0, 0.5, persist=persist) == STATUS_BLOCKED_ON_EVIDENCE
    assert job_b["status"] == STATUS_BLOCKED_ON_EVIDENCE
    persist.assert_called_once_with(job_b)
    persist.reset_mock()

    # Test C: Hoher PE
    for pe in (0.8, 0.9):
        job_c: Dict[str, Any] = {"job_id": "job_1", "status": "processing"}
        assert evaluate_evidence(job_c, 5, pe, persist=persist) == STATUS_BLOCKED_ON_EVIDENCE
        assert job_c["status"] == STATUS_BLOCKED_ON_EVIDENCE
        persist.assert_called_once_with(job_c)
        persist.reset_mock()
