import os
import hmac
import hashlib
import unittest
from src.logic_core.agent_isolation import SafeExecMembrane, CORE_WEBHOOK_SECRET

class TestIsolation(unittest.TestCase):
    def test_network_veto(self):
        membrane = SafeExecMembrane()
        
        code_payload = """
import os
exit_code = os.system("curl --connect-timeout 2 google.com")
if exit_code == 0:
    print("SUCCESS")
else:
    print("FAILED")
"""
        causal_hash_t = hmac.new(CORE_WEBHOOK_SECRET, code_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        
        try:
            output = membrane.execute_in_cell(code_payload, causal_hash_t)
            self.assertNotIn("SUCCESS", output)
            self.assertTrue("FAILED" in output or "ERROR" in output)
        except RuntimeError as e:
            self.assertIn("Docker", str(e))
