
import os
import requests
from dotenv import load_dotenv

load_dotenv()

auth_url = os.getenv("SYNAPT_AUTH_BASE")
mcp_url = os.getenv("SYNAPT_MCP_URL")
username = os.getenv("SYNAPT_USERNAME")
password = os.getenv("SYNAPT_PASSWORD")

if not all([auth_url, mcp_url, username, password]):
    raise RuntimeError("One or more required SYNAPT_* variables are missing.")

# 1. Request a fresh access token.
try:
    login = requests.post(
        auth_url,
        data={"username": username, "password": password},
        timeout=30,
    )

    print("Authentication HTTP status:", login.status_code)

    if not login.ok:
        print("Authentication response:", login.text[:1500])
        raise SystemExit("Could not obtain a fresh token.")

    result = login.json()
    token = result.get("access_token")

    if not token:
        print("Response fields:", list(result.keys()))
        raise SystemExit(
            "No access_token returned. Check the authentication response."
        )

    print("Fresh access token received; value hidden.")

except requests.RequestException as exc:
    raise SystemExit(f"Authentication request failed: {exc}")

# 2. Test MCP initialization with the fresh token.
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "supply-chain-retriever",
            "version": "1.0.0",
        },
    },
}

try:
    response = requests.post(
        mcp_url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    print("\nMCP HTTP status:", response.status_code)
    print("MCP Content-Type:", response.headers.get("Content-Type"))
    print("MCP session:", response.headers.get("Mcp-Session-Id"))
    print("MCP response:", response.text[:2500])

    if response.ok:
        print(
            "\nThe fresh token was accepted at the HTTP layer. "
            "Check the response for a successful MCP initialization."
        )

except requests.RequestException as exc:
    print("MCP request failed:", str(exc))