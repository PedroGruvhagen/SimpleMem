#!/usr/bin/env python3
"""
SimpleMem MCP Stdio-to-HTTP Bridge

This script bridges Claude Desktop's stdio-based MCP protocol to
SimpleMem's HTTP-based MCP server.

Usage:
  python stdio_bridge.py --token YOUR_BEARER_TOKEN [--url http://127.0.0.1:8000/mcp]
"""

import sys
import json
import argparse
import urllib.request
import urllib.error

# Global session ID - captured from initialize response
session_id = None


def send_to_server(url: str, token: str, message: dict) -> dict:
    """Send a JSON-RPC message to the HTTP MCP server"""
    global session_id

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/event-stream",
    }

    # Add session ID if we have one (required after initialize)
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    data = json.dumps(message).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            # Capture session ID from response headers
            new_session_id = response.headers.get("Mcp-Session-Id")
            if new_session_id:
                session_id = new_session_id

            content_type = response.headers.get("Content-Type", "")
            body = response.read().decode("utf-8")

            # Handle SSE responses (text/event-stream)
            if "text/event-stream" in content_type:
                # Parse SSE - collect all data: lines
                results = []
                for line in body.split("\n"):
                    line = line.strip()
                    if line.startswith("data:"):
                        json_str = line[5:].strip()
                        if json_str:
                            try:
                                results.append(json.loads(json_str))
                            except json.JSONDecodeError:
                                pass
                # Return last result (usually the final response)
                return results[-1] if results else None
            else:
                # Regular JSON response
                if body.strip():
                    return json.loads(body)
                return None

    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")
        except:
            error_body = str(e)

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32000,
                "message": f"HTTP {e.code}: {error_body}"
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }


def main():
    parser = argparse.ArgumentParser(description="SimpleMem stdio-to-HTTP bridge")
    parser.add_argument("--token", required=True, help="Bearer token for authentication")
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp", help="MCP server URL")
    args = parser.parse_args()

    # Read JSON-RPC messages from stdin, forward to HTTP server, write responses to stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            message = json.loads(line)
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            }
            print(json.dumps(error_response), flush=True)
            continue

        # Forward to HTTP server
        response = send_to_server(args.url, args.token, message)

        # Only send response for requests (not notifications)
        if response and message.get("id") is not None:
            print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()
