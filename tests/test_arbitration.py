import pytest
from typing import List, Dict, Any

from src.logic_core.arbitration_engine import (
    get_next_job,
    commit_job_result,
    check_liveness,
    evaluate_evidence,
    MergeConflictError,
    EntropicDeadlockError,
    _reset_jobs_db
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
    """Trap 2: Single-Job Merge Rule (First-Wins & Jahn-Teller)"""
    _reset_jobs_db()

    # Test A: First Commit
    success = commit_job_result("job_alpha", {"data": 42}, 0.95)
    assert success is True

    # Test B: Late Arriver (MergeConflictError)
    with pytest.raises(MergeConflictError):
        commit_job_result("job_alpha", {"data": 43}, 0.95)
        
    # Test C: Jahn-Teller-Symmetriebruch / Anti-0.5
    with pytest.raises(EntropicDeadlockError):
        commit_job_result("job_beta", {"data": 1}, 0.50)
        
    with pytest.raises(EntropicDeadlockError):
        commit_job_result("job_gamma", {"data": 1}, 0.49)
        
    with pytest.raises(EntropicDeadlockError):
        commit_job_result("job_delta", {"data": 1}, 0.51)

def test_liveness_monitor():
    """Trap 3: Liveness Monitor (Heartbeat)"""
    # check_liveness(job_id: str, last_heartbeat: float, current_time: float, timeout: float) -> str
    
    # Test A: Alive
    assert check_liveness("job_1", 100.0, 105.0, 10.0) == "processing"
    
    # Test B: Dead
    assert check_liveness("job_1", 100.0, 110.0, 10.0) == "failed"
    assert check_liveness("job_1", 100.0, 115.0, 10.0) == "failed"

def test_evaluate_evidence():
    """Trap 4: A10 Occam's Negative Razor (Evidenz & PE)"""
    # evaluate_evidence(job_id: str, available_vectors: int, internal_prediction_error: float) -> str
    
    # Test A: Ausreichend Evidenz
    assert evaluate_evidence("job_1", 5, 0.5) == "processing"
    
    # Test B: Evidenz erschöpft
    assert evaluate_evidence("job_1", 0, 0.5) == "blocked_on_evidence"
    
    # Test C: Hoher PE
    assert evaluate_evidence("job_1", 5, 0.8) == "blocked_on_evidence"
    assert evaluate_evidence("job_1", 5, 0.9) == "blocked_on_evidence"
