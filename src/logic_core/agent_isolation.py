import os
import hmac
import hashlib
import docker
import base64
import threading
from loguru import logger

CORE_WEBHOOK_SECRET = os.getenv("CORE_WEBHOOK_SECRET", "dummy-secret-key").encode("utf-8")

def verify_hmac(payload: str, expected_hash: str) -> bool:
    """Verifies the HMAC signature of the payload."""
    payload_bytes = payload.encode("utf-8")
    computed_hmac = hmac.new(CORE_WEBHOOK_SECRET, payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed_hmac, expected_hash)

class SafeExecMembrane:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.warning(f"Failed to initialize Docker client: {e}")
            self.client = None

    def execute_in_cell(self, code_payload: str, causal_hash_t: str) -> str:
        """
        Executes code in an ephemeral, isolated Docker container.
        Enforces Zero Trust and Anti-Heroin axioms.
        """
        if not verify_hmac(code_payload, causal_hash_t):
            error_msg = "SECURITY VIOLATION: Invalid causal_hash_t signature. Replay or tampering detected."
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not self.client:
            raise RuntimeError("Docker client not available.")

        image_name = "omega-agent-base"
        encoded_payload = base64.b64encode(code_payload.encode("utf-8")).decode("utf-8")
        command = f"python3 -c \"import base64; exec(base64.b64decode('{encoded_payload}').decode('utf-8'))\""

        # Zwingend required by plan:
        # network_disabled=True, no mounts, remove=True
        # Resource limits: cpus=0.49, mem_limit="256m"
        
        container = None
        
        # We use a trick to enforce timeout while keeping remove=True
        # We start detached, and poll
        try:
            container = self.client.containers.run(
                image=image_name,
                command=command,
                network_disabled=True,
                remove=True,               # strictly from plan
                detach=True,               
                mem_limit="256m",          
                nano_cpus=int(0.49 * 1e9)  
            )
        except Exception as e:
            logger.error(f"Failed to start execution cell: {e}")
            return f"ERROR: Could not start cell: {e}"

        # Wait with timeout
        try:
            # We must get logs *before* it gets removed, or we use the `logs` stream, or we rely on `logs()` if it hasn't been removed yet.
            # But wait, with remove=True and detach=True, as soon as the container finishes, Docker daemon deletes it and its logs.
            # So `container.logs()` will fail if called after it stops.
            # We must stream logs while it is running.
            
            output = []
            
            # Use a thread to collect logs to not block the timeout checks
            def collect_logs():
                try:
                    for line in container.logs(stream=True, stdout=True, stderr=True):
                        output.append(line.decode('utf-8'))
                except docker.errors.APIError:
                    pass
                except Exception:
                    pass

            log_thread = threading.Thread(target=collect_logs, daemon=True)
            log_thread.start()
            
            # Wait loop with timeout
            import time
            start_time = time.time()
            timeout = 30
            timeout_exceeded = False
            
            while True:
                try:
                    container.reload()
                except docker.errors.NotFound:
                    # Container is gone, which means it finished and was removed by Docker.
                    break
                except docker.errors.APIError:
                    break
                    
                if container.status not in ["created", "running"]:
                    break
                    
                if time.time() - start_time > timeout:
                    timeout_exceeded = True
                    logger.error("TIMEOUT (Apoptosis): Container exceeded 30s. Sending SIGKILL.")
                    try:
                        container.kill()
                    except docker.errors.APIError:
                        pass
                    break
                
                time.sleep(0.1)
                
            log_thread.join(timeout=1.0)
            
            if timeout_exceeded:
                return "ERROR: Timeout exceeded. Container killed (Apoptosis)."
            
            return "".join(output)

        except Exception as e:
            logger.error(f"Error reading container logs: {e}")
            return f"ERROR: Execution failed: {e}"
