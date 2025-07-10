import os

# Test Configuration
DEFAULT_PORT = 8000
DEFAULT_HOST = "localhost"

# Get port from environment variable or use default
PORT = int(os.getenv("PORT", DEFAULT_PORT))
HOST = os.getenv("HOST", DEFAULT_HOST)

# Construct base URL
BASE_URL = f"http://{HOST}:{PORT}" 