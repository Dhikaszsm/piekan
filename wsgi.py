# WSGI entry point untuk production deployment
import os
import sys

# Add project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from app import app

# Configuration untuk production
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'your-production-secret-key'),
    DEBUG=False,
    TESTING=False,
)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
