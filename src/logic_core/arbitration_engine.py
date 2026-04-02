from typing import List, Dict, Any

class MergeConflictError(Exception):
    """Raised when a late arriver tries to commit a result for an already completed job."""
    pass

class EntropicDeadlockError(Exception):
    """Raised when confidence hits the 0.5 static dead zone (0.49 <= conf <= 0.51)."""
    pass

# Simple mock state for testing
_completed_jobs = set()

def _reset_jobs_db() -> None:
    """Resets the internal job database for tests."""
    global _completed_jobs
    _completed_jobs.clear()

def get_next_job(queue: List[Dict[str, Any]], available_workers: int) -> List[Dict[str, Any]]:
    """
    Trap 1: Priority Scheduler.
    Sort by priority (int, ascending: 1 is high) and then expected_arrival (float, ascending).
    Already processing jobs must not be replaced.
    """
    running_jobs = [job for job in queue if job.get("status") == "processing"]
    pending_jobs = [job for job in queue if job.get("status") == "pending"]
    
    # Sort pending jobs: priority first, expected_arrival second
    pending_jobs.sort(key=lambda x: (x.get("priority", 999), x.get("expected_arrival", float('inf'))))
    
    assigned = []
    
    # Assign running jobs first (starvation protection)
    for job in running_jobs:
        if len(assigned) < available_workers:
            assigned.append(job)
            
    # Fill remaining slots with highest priority pending jobs
    for job in pending_jobs:
        if len(assigned) < available_workers:
            assigned.append(job)
            
    return assigned

def commit_job_result(job_id: str, result_data: Dict[str, Any], resonance_confidence: float) -> bool:
    """
    Trap 2: Single-Job Merge Rule.
    First-Wins, rejects late arrivers, and guards against the 0.5 static dead zone.
    """
    # Test C: Jahn-Teller Symmetriebruch / Anti-0.5
    if 0.49 <= resonance_confidence <= 0.51:
        raise EntropicDeadlockError(f"Confidence {resonance_confidence} is in the 0.5 dead zone. No merge allowed.")
        
    global _completed_jobs
    
    # Test B: Late Arriver
    if job_id in _completed_jobs:
        raise MergeConflictError(f"Job {job_id} is already committed. Late arriver rejected.")
        
    # Test A: First commit
    _completed_jobs.add(job_id)
    return True

def check_liveness(job_id: str, last_heartbeat: float, current_time: float, timeout: float) -> str:
    """
    Trap 3: Liveness Monitor.
    If the time since the last heartbeat is >= timeout, the job has failed.
    """
    if current_time - last_heartbeat >= timeout:
        return "failed"
    return "processing"

def evaluate_evidence(job_id: str, available_vectors: int, internal_prediction_error: float) -> str:
    """
    Trap 4: A10 Occam's Negative Razor.
    If evidence is exhausted or internal PE is too high, the job stops.
    """
    if available_vectors == 0:
        return "blocked_on_evidence"
    if internal_prediction_error >= 0.8:
        return "blocked_on_evidence"
    return "processing"
