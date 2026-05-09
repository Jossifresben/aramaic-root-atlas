import pytest
import sys
import os

# Disable rate limits for the test suite — every test would otherwise
# count against the same IP's quota and trip the limiter. Real rate-limit
# behaviour is covered by tests/test_api_versioning.py with explicit
# overrides on a separate test client.
os.environ.setdefault('API_RATE_LIMIT_DISABLED', '1')

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app as flask_app


@pytest.fixture(scope='session')
def client():
    flask_app.app.config['TESTING'] = True
    with flask_app.app.test_client() as c:
        yield c
