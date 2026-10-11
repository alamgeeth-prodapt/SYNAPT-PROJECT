
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = os.getenv("SYNAPT_AUTH_BASE")
MCP_URL = os.getenv("SYNAPT_MCP_URL")
USERNAME = os.getenv("SYNAPT_USERNAME")
PASSWORD = os.getenv("SYNAPT_PASSWORD")

if not all([AUTH_URL, MCP_URL, USERNAME, PASSWORD]):
    raise RuntimeError("Missing Synapt authentication settings in .env")


def parse_response(response):
    """Parse a JSON or SSE response without printing credentials."""
    content_type = response.headers.get("Content-Type", "")

    if "text/event-stream" in content_type:
        results = []
        for line in response.text.splitlines():
            if line.startswith("data:"):
                data = line[len("data:"):].strip()
                if data:
                    try:
                        results.append(json.loads(data))
                    except json.JSONDecodeError:
                        print("Received a non-JSON SSE event.")
        return results

    try:
        return [response.json()]
    except ValueError:
        print("Non-JSON response:", response.text[:1000])
        return []


def send_rpc(headers, method, request_id=None, params=None):
    payload = {
        "jsonrpc": "2.0",
        "method": method,
    }

    if request_id is not None:
        payload["id"] = request_id

    if params is not None:
        payload["params"] = params

    response = requests.post(
        MCP_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )

    print(f"{method}: HTTP {response.status_code}")
    response.raise_for_status()
    return parse_response(response)

provider_id = os.getenv("SYNAPT_PROVIDER_ID")

if not provider_id:
    raise RuntimeError("SYNAPT_PROVIDER_ID is missing from .env")


def call_tool(tool_name, arguments, request_id):
    results = send_rpc(
        headers,
        "tools/call",
        request_id=request_id,
        params={
            "name": tool_name,
            "arguments": arguments,
        },
    )

    for item in results:
        if "error" in item:
            print("MCP error:", item["error"])
            continue

        result = item.get("result", {})
        print(f"\n--- {tool_name} ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))

    return results


# First verify that this provider is accessible.



# 1. Authenticate.
login = requests.post(
    AUTH_URL,
    data={"username": USERNAME, "password": PASSWORD},
    timeout=30,
)
print("Authentication:", login.status_code)
login.raise_for_status()

token = login.json().get("access_token")
if not token:
    raise RuntimeError("Authentication response did not contain access_token.")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}

# 2. Initialize MCP.
init_results = send_rpc(
    headers,
    "initialize",
    request_id=1,
    params={
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "supply-chain-retriever",
            "version": "1.0.0",
        },
    },
)

for item in init_results:
    if "error" in item:
        raise RuntimeError(f"MCP initialization failed: {item['error']}")
    if "result" in item:
        print("Server info:", item["result"].get("serverInfo"))
        print("Protocol:", item["result"].get("protocolVersion"))

# 3. Complete the MCP handshake.
send_rpc(headers, "notifications/initialized")

# 4. Discover tools.
tool_results = send_rpc(headers, "tools/list", request_id=2)

tools_found = False

for item in tool_results:
    if "error" in item:
        print("MCP error:", item["error"])
        continue

    result = item.get("result", {})
    tools = result.get("tools", [])

    if tools:
        tools_found = True
        print(f"\nAvailable MCP tools ({len(tools)}):")

        for tool in tools:
            print(f"\n- {tool.get('name')}")
            print(f"  Description: {tool.get('description', 'No description')}")
            print("  Input schema:")
            print(json.dumps(tool.get("inputSchema", {}), indent=2))

    elif "tools" in result:
        tools_found = True
        print("The server returned an empty tools list.")

if not tools_found:
    print(
        "\nNo tools list was found in the response. "
        "Share the redacted HTTP statuses and response structure."
    )

call_tool(
    "trident_get_stats",
    {"provider_id": provider_id},
    3,
)

# Then test contextual retrieval.
call_tool(
    "trident_query",
    {
        "provider_id": provider_id,
        "question": (
            "What factors are associated with severe supply chain "
            "disruptions, and what recovery strategies are described "
            "in the available knowledge?"
        ),
        "top_k": 5,
    },
    4,
)