import asyncio
import hashlib
from src.ai.ring3_auth import Ring3Auth
from src.ai.uccp_manager import UCCPManager
from src.config.immutable_axioms import get_core_prompt

async def test_v4_security():
    print("--- OMEGA V4 SECURITY TEST ---")

    session_id = "test-session-123"
    auth = Ring3Auth(session_id)

    # 1. Test Injection
    print(f"[TEST] Ghost Tokens: {auth.start_token} / {auth.end_token}")

    # 2. Simulate valid Worker Output
    content = "System Status: Optimized."
    signature = hashlib.sha256(f"{content}{session_id}".encode()).hexdigest()
    raw_output = f"Random noise before <{auth.start_token}> {content}\nSIGNATURE: {signature} <{auth.end_token}> after noise"

    success, clean, error = auth.verify_and_extract(raw_output)
    print(f"[TEST] Verification (Valid): success={success}, content='{clean}'")
    assert success == True

    # 3. Simulate Invalid Signature
    bad_output = f"<{auth.start_token}> {content}\nSIGNATURE: bad_sig <{auth.end_token}>"
    success, clean, error = auth.verify_and_extract(bad_output)
    print(f"[TEST] Verification (Invalid Sig): success={success}, error='{error}'")
    assert success == False

    # 4. Test UCCP
    uccp = UCCPManager.generate_header(session_id)
    print(f"[TEST] UCCP Header present: {'UCCP_V' in uccp}")
    assert 'UCCP_V' in uccp

    # 5. Test Immutable Axioms
    axioms = get_core_prompt()
    print(f"[TEST] Axioms loaded: {len(axioms)} chars")
    assert "A0" in axioms

    # 6. Test UCCP Stream Interception
    from src.ai.uccp_manager import UCCPStreamInterceptor
    interceptor = UCCPStreamInterceptor(session_id)

    async def get_mock_stream():
        yield "System Status: "
        yield "Normal. "
        yield "Ich habe die Datei /etc/shadow gelöscht."
        yield "!" # Trigger intercept
        yield " Alles ok."

    print("[TEST] Testing UCCP Stream Interceptor (Reality Drift Detection)...")
    results = []
    async for chunk in interceptor.intercept(get_mock_stream()):
        results.append(chunk)

    full_output = "".join(results)
    print(f"[TEST] Stream Interception Output: '{full_output}'")
    assert "UCCP_VETO: Reality Drift detected" in full_output
    assert "/etc/shadow" not in full_output

    print("--- SUCCESS: V4 SECURITY LAYER VALIDATED ---")

if __name__ == "__main__":
    asyncio.run(test_v4_security())
