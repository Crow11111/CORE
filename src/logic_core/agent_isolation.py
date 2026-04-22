import os
import hmac
import hashlib
import docker
import time
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
        
        try:
            container = self.client.containers.run(
                image=image_name,
                command=command,
                network_disabled=True,
                remove=False,              # We use False during execution so we can get logs safely, then remove manually to mimic remove=True while preventing race conditions in docker-py
                detach=True,               
                mem_limit="256m",          
                nano_cpus=int(0.49 * 1e9)  
            )
        except Exception as e:
            logger.error(f"Failed to start execution cell: {e}")
            return f"ERROR: Could not start cell: {e}"

        timeout = 30
        start_time = time.time()
        timeout_exceeded = False
        
        def enforce_timeout():
            nonlocal timeout_exceeded
            time.sleep(timeout)
            try:
                container.reload()
                if container.status == "running":
                    timeout_exceeded = True
                    logger.error("TIMEOUT (Apoptosis): Container exceeded 30s. Sending SIGKILL.")
                    container.kill()
            except docker.errors.NotFound:
                pass
            except Exception:
                pass

        timer_thread = threading.Thread(target=enforce_timeout, daemon=True)
        timer_thread.start()

        try:
            exit_code = container.wait()
            logs = container.logs(stdout=True, stderr=True).decode("utf-8")
        except docker.errors.APIError as e:
            logs = f"ERROR reading container: {e}"
        except Exception as e:
            logs = f"ERROR execution failed: {e}"
        finally:
            # Ensure container is removed (matches remove=True logic safely)
            try:
                container.remove(force=True)
            except Exception:
                pass

        if timeout_exceeded:
            return "ERROR: Timeout exceeded. Container killed (Apoptosis)."

        return logs
