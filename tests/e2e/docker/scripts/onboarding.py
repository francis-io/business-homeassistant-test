import argparse
import http.client
import json
import time
import logging
from urllib.parse import urlparse
import os
import sys

# ------------------ CLI Argument Parsing ------------------
parser = argparse.ArgumentParser(description="Home Assistant onboarding script")

parser.add_argument("--base-url", default="http://localhost:8123", help="Base URL of the Home Assistant instance")
parser.add_argument("--username", default="admin", help="Username for the user")
parser.add_argument("--password", default="admin", help="Password for the user")
parser.add_argument("--name", default="admin", help="Full name of the user")
parser.add_argument("--language", default="en", help="Language (e.g. 'en')")
parser.add_argument("--timezone", default="UTC", help="Timezone (e.g. 'UTC')")
parser.add_argument("--location-name", default="Home", help="Name of the location")
parser.add_argument("--latitude", type=float, default=0.0, help="Latitude")
parser.add_argument("--longitude", type=float, default=0.0, help="Longitude")
parser.add_argument("--unit-system", choices=["metric", "imperial"], default="metric", help="Unit system")
parser.add_argument("--currency", default="gbp", help="Currency code (e.g. gbp, usd)")
parser.add_argument("--country", default="gb", help="Country code (e.g. gb, us)")
parser.add_argument("--elevation", type=int, default=0, help="Elevation in meters")
parser.add_argument("--log-level", default="DEBUG", help="Log level (DEBUG, INFO, etc.)")
parser.add_argument("--wait-timeout", type=int, default=60, help="Max seconds to wait for server to respond")

args = parser.parse_args()

# ------------------ Configuration ------------------
BASE_URL      = args.base_url
CLIENT_ID     = BASE_URL
USERNAME      = args.username
PASSWORD      = args.password
NAME          = args.name
LANGUAGE      = args.language
TIMEZONE      = args.timezone
LOCATION_NAME = args.location_name
LATITUDE      = args.latitude
LONGITUDE     = args.longitude
UNIT_SYSTEM   = args.unit_system
CURRENCY      = args.currency
COUNTRY       = args.country
ELEVATION     = args.elevation
LOG_LEVEL     = args.log_level.upper()
WAIT_TIMEOUT  = args.wait_timeout

RETRY_INTERVAL = 1
MAX_RETRIES = 5
HTTP_TIMEOUT = 5
TOKEN_FILE    = "/tmp/onboarding_token.json"

# ------------------ Logging ------------------
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.DEBUG),
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

# ------------------ Connection Helpers ------------------
parsed_url = urlparse(BASE_URL)
conn_class = http.client.HTTPSConnection if parsed_url.scheme == "https" else http.client.HTTPConnection

if not parsed_url.hostname or not parsed_url.port:
    raise ValueError(f"Invalid BASE_URL: {BASE_URL}")

def with_http_connection(func):
    def wrapper(*args, **kwargs):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                conn = conn_class(parsed_url.hostname, parsed_url.port, timeout=HTTP_TIMEOUT)
                return func(conn, *args, **kwargs)
            except Exception as e:
                log.warning(f"{func.__name__} failed (attempt {attempt}): {e}")
                if attempt == MAX_RETRIES:
                    raise
                time.sleep(RETRY_INTERVAL * attempt)
    return wrapper

def wait_for_server():
    log.info(f"Waiting for server to respond at {BASE_URL} (max {WAIT_TIMEOUT}s)...")
    deadline = time.time() + WAIT_TIMEOUT
    while time.time() < deadline:
        try:
            conn_class = http.client.HTTPSConnection if parsed_url.scheme == "https" else http.client.HTTPConnection
            conn = conn_class(parsed_url.hostname, parsed_url.port, timeout=HTTP_TIMEOUT)
            conn.request("GET", "/")
            resp = conn.getresponse()
            if resp.status in (200, 302):
                log.info("Server is up")
                return
        except Exception as e:
            log.debug(f"Waiting for server: {e}")
        time.sleep(RETRY_INTERVAL)
    raise TimeoutError(f"Timed out after {WAIT_TIMEOUT}s waiting for server.")

@with_http_connection
def api_request(conn, method, path, body=None, headers=None):
    headers = headers or {}
    request_body = json.dumps(body) if body else None
    if request_body:
        headers['Content-Type'] = 'application/json'

    log.debug(f"{method} {path} headers={headers} body={request_body}")
    conn.request(method, path, body=request_body, headers=headers)
    resp = conn.getresponse()
    resp_data = resp.read().decode()

    if resp.status >= 400:
        log.error(f"HTTP {resp.status} {resp.reason}: {resp_data}")
        raise Exception(f"HTTP {resp.status}: {resp.reason}")

    if resp_data:
        try:
            return json.loads(resp_data)
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON: {e} body={resp_data}")
            raise
    return {}

def get_status():
    return api_request("GET", "/api/onboarding")

def create_user():
    return api_request("POST", "/api/onboarding/users", {
        "client_id": CLIENT_ID,
        "name": NAME,
        "username": USERNAME,
        "password": PASSWORD,
        "language": LANGUAGE
    })["auth_code"]

@with_http_connection
def exchange_token(conn, code):
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                log.info("Reusing existing access token from /tmp")
                return data["access_token"]
        except Exception:
            pass  # fall back to full flow if file is corrupt

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    body = f"grant_type=authorization_code&code={code}&client_id={CLIENT_ID}"
    conn.request("POST", "/auth/token", body=body, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode()

    if resp.status != 200:
        raise Exception(f"Token exchange failed: HTTP {resp.status} {resp.reason}")

    try:
        token_data = json.loads(raw)
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f)
        return token_data["access_token"]
    except Exception as e:
        log.error(f"Error parsing token response: {e} raw={raw}")
        raise

def submit_core(token):
    api_request("POST", "/api/onboarding/core_config", {
        "location_name": LOCATION_NAME,
        "time_zone": TIMEZONE,
        "unit_system": UNIT_SYSTEM,
        "currency": CURRENCY,
        "country": COUNTRY,
        "language": LANGUAGE,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "elevation": ELEVATION
    }, headers={"Authorization": f"Bearer {token}"})

def submit_analytics(token):
    api_request("POST", "/api/onboarding/analytics", {
        "preferences": {"base": False, "diagnostics": False, "usage": False}
    }, headers={"Authorization": f"Bearer {token}"})

def submit_integration(token):
    api_request("POST", "/api/onboarding/integration", {
        "client_id": CLIENT_ID,
        "redirect_uri": f"{BASE_URL}/lovelace"
    }, headers={"Authorization": f"Bearer {token}"})

def main():
    wait_for_server()
    status = get_status()
    log.debug(f"Status: {status}")
    steps = {s["step"]: s["done"] for s in status}

    if not steps.get("user"):
        log.info("Creating user...")
        auth_code = create_user()
        token = exchange_token(auth_code)
    else:
        log.warning("User step already completed. Exiting.")
        return

    if not steps.get("core_config"):
        log.info("Submitting core config...")
        submit_core(token)

    if not steps.get("analytics"):
        log.info("Submitting analytics...")
        submit_analytics(token)

    if not steps.get("integration"):
        log.info("Completing integration...")
        submit_integration(token)

    final = get_status()
    if all(s["done"] for s in final):
        log.info(f"Onboarding complete. Credentials: {USERNAME} / {PASSWORD}")
        sys.exit(0)  # Success
    else:
        remaining = [s["step"] for s in final if not s["done"]]
        log.warning(f"Onboarding incomplete. Remaining steps: {remaining}")
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
