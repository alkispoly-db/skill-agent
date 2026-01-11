#!/usr/bin/env python3
"""
Interactive CLI client for the Marketing Research Agent API.

This script connects to a running FastAPI server and provides an interactive
chat interface. It maintains conversation history for context across messages.

Usage:
    python chat_cli.py                      # Connect to localhost:5000
    python chat_cli.py --host localhost     # Specify host
    python chat_cli.py --port 8000          # Specify port
    python chat_cli.py --url http://localhost:5000  # Full URL
    python chat_cli.py --url https://app.databricksapps.com --databricks-profile DEFAULT
"""
import argparse
import os
import sys
from typing import List, Dict, Optional
import requests


def get_databricks_auth_header(profile: Optional[str] = None) -> Dict[str, str]:
    """
    Get authentication header using Databricks SDK configuration.

    Args:
        profile: Optional Databricks CLI profile name

    Returns:
        Dictionary with Authorization header

    Raises:
        ImportError: If databricks-sdk is not installed
        Exception: If authentication setup fails
    """
    try:
        from databricks.sdk import WorkspaceClient
        from databricks.sdk.core import Config
    except ImportError:
        raise ImportError(
            "databricks-sdk is required for Databricks authentication.\n"
            "Install it with: pip install databricks-sdk"
        )

    try:
        # Create config with profile if specified
        if profile:
            os.environ["DATABRICKS_CONFIG_PROFILE"] = profile
            config = Config(profile=profile)
        else:
            config = Config()

        # Get credentials from the config
        auth_headers = config.authenticate()

        # The authenticate() method returns a dict of headers
        if isinstance(auth_headers, dict):
            # Check if it has Authorization header
            if "Authorization" in auth_headers:
                return {"Authorization": auth_headers["Authorization"]}

            # Check case-insensitive
            for key, value in auth_headers.items():
                if key.lower() == "authorization":
                    return {"Authorization": value}

            # If no Authorization header, return the whole dict
            # (it might be in a different format)
            return auth_headers

        raise Exception(
            f"Unexpected auth response type: {type(auth_headers)}. "
            "Expected dict with Authorization header."
        )

    except Exception as e:
        raise Exception(
            f"Failed to authenticate with Databricks: {e}\n"
            f"Make sure you have configured Databricks CLI with: databricks configure --token"
        )


def print_banner(base_url: str):
    """Print the welcome banner."""
    print("=" * 60)
    print("Marketing Research Agent - Interactive Client")
    print("=" * 60)
    print(f"Connected to: {base_url}")
    print("\nAsk me about product research! Type 'exit' or 'quit' to end.")
    print("Type 'clear' to reset conversation history.\n")


def send_message(
    base_url: str,
    messages: List[Dict[str, str]],
    token: str = None,
    auth_headers: Dict[str, str] = None
) -> str:
    """
    Send messages to the API and get a response.

    Args:
        base_url: The base URL of the API server
        messages: List of message dicts with 'role' and 'content'
        token: Optional OAuth2 bearer token for authentication
        auth_headers: Optional auth headers dict (e.g., from Databricks SDK)

    Returns:
        The assistant's response content

    Raises:
        requests.RequestException: If the request fails
        ValueError: If the response format is invalid
    """
    url = f"{base_url}/api/v1/chat/completions"

    payload = {
        "messages": messages,
    }

    headers = {"Content-Type": "application/json"}

    # Add authentication - prioritize auth_headers over token
    if auth_headers:
        headers.update(auth_headers)
    elif token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=120,  # 2 minute timeout for long-running requests
        )
        response.raise_for_status()

        data = response.json()

        # Extract the assistant's message from OpenAI-compatible response
        if "choices" not in data or not data["choices"]:
            raise ValueError("Invalid response format: missing choices")

        choice = data["choices"][0]
        if "message" not in choice or "content" not in choice["message"]:
            raise ValueError("Invalid response format: missing message content")

        return choice["message"]["content"]

    except requests.Timeout:
        raise Exception(
            "Request timed out. The server might be processing a complex request."
        )
    except requests.ConnectionError:
        raise Exception(
            f"Could not connect to {base_url}. "
            "Make sure the server is running with: uvicorn app:app --host 0.0.0.0 --port 5000"
        )
    except requests.HTTPError as e:
        if e.response is not None:
            try:
                error_detail = e.response.json()
                raise Exception(f"API error: {error_detail}")
            except ValueError:
                raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        raise Exception(f"HTTP error: {e}")


def run_interactive(base_url: str, token: str = None, auth_headers: Dict[str, str] = None):
    """
    Run the interactive chat loop.

    Args:
        base_url: The base URL of the API server
        token: Optional OAuth2 bearer token for authentication
        auth_headers: Optional auth headers dict (e.g., from Databricks SDK)
    """
    print_banner(base_url)

    # Maintain conversation history
    messages: List[Dict[str, str]] = []

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nThanks for using Marketing Research Agent!")
                break

            if user_input.lower() == "clear":
                messages = []
                print("\n[Conversation history cleared]\n")
                continue

            if not user_input:
                continue

            # Add user message to history
            messages.append({"role": "user", "content": user_input})

            # Send request and get response
            print("\nAgent: ", end="", flush=True)
            try:
                response_content = send_message(base_url, messages, token, auth_headers)
                print(response_content)

                # Add assistant response to history
                messages.append({"role": "assistant", "content": response_content})

            except Exception as e:
                print(f"\n[Error: {e}]")
                # Remove the user message since we couldn't get a response
                messages.pop()

            print()  # Empty line for readability

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except EOFError:
            print("\n\nGoodbye!")
            break


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive client for Marketing Research Agent API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Connect to default server (localhost:5000)
  python chat_cli.py

  # Connect to custom host
  python chat_cli.py --host 192.168.1.100

  # Connect to custom port
  python chat_cli.py --port 8000

  # Connect to Databricks Apps with profile (recommended)
  python chat_cli.py --url https://your-app.databricksapps.com --databricks-profile DEFAULT

  # Connect to Databricks Apps with token
  python chat_cli.py --url https://your-app.databricksapps.com --token dapi...
        """,
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="API server host (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="API server port (default: 5000)",
    )
    parser.add_argument(
        "--url",
        help="Full API base URL (overrides --host and --port)",
    )
    parser.add_argument(
        "--token",
        help="OAuth2 bearer token for authentication",
    )
    parser.add_argument(
        "--databricks-profile",
        help="Databricks CLI profile name (e.g., DEFAULT). Uses Databricks SDK authentication.",
    )

    args = parser.parse_args()

    # Determine base URL
    if args.url:
        base_url = args.url.rstrip("/")
    else:
        base_url = f"http://{args.host}:{args.port}"

    # Get authentication headers if using Databricks profile
    auth_headers = None
    if args.databricks_profile:
        try:
            print(f"Using Databricks profile: {args.databricks_profile}")
            auth_headers = get_databricks_auth_header(args.databricks_profile)
            print("✓ Databricks authentication configured")
        except Exception as e:
            print(f"\nError: {e}", file=sys.stderr)
            sys.exit(1)

    # Verify server is reachable
    try:
        print(f"Connecting to {base_url}...")
        headers = {}
        if auth_headers:
            headers.update(auth_headers)
        elif args.token:
            headers["Authorization"] = f"Bearer {args.token}"

        response = requests.get(f"{base_url}/api/v1/healthcheck", headers=headers, timeout=5)
        response.raise_for_status()
        print("Connection successful!\n")
    except requests.RequestException as e:
        print(f"\nError: Could not connect to {base_url}", file=sys.stderr)
        if not args.token and not args.databricks_profile and "databricks" in base_url.lower():
            print("\nNote: Databricks Apps require authentication.", file=sys.stderr)
            print("Use: python chat_cli.py --url <URL> --databricks-profile DEFAULT", file=sys.stderr)
            print("Or: python chat_cli.py --url <URL> --token <TOKEN>\n", file=sys.stderr)
        else:
            print(
                f"\nMake sure the server is running with:",
                file=sys.stderr,
            )
            print(f"  uvicorn app:app --host 0.0.0.0 --port {args.port}\n", file=sys.stderr)
        sys.exit(1)

    # Run interactive mode
    run_interactive(base_url, args.token, auth_headers)


if __name__ == "__main__":
    main()
