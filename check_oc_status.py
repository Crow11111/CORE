import sys
import os

# Add src to python path to allow importing from src.network
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from network.openclaw_client import check_gateway, is_configured, VPS_HOST, OPENCLAW_GATEWAY_PORT
except ImportError as e:
    print(f'Error importing openclaw_client: {e}')
    sys.exit(1)

print(f'--- Diagnose Start ---')
print(f'Configured: {is_configured()}')
print(f'Host: {VPS_HOST}')
print(f'Port: {OPENCLAW_GATEWAY_PORT}')

if not is_configured():
    print('SKIPPING CHECK: Not configured.')
    sys.exit(0)

print(f'Checking Gateway...')
success, msg = check_gateway(timeout=10.0)
print(f'Success: {success}')
print(f'Message: {msg}')
print(f'--- Diagnose End ---')
