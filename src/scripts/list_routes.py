import requests
from src.api.main import app

for route in app.routes:
    print(f"Path: {route.path} | Methods: {route.methods}")
