#!/usr/bin/env python3
"""
Entry point script to run the marketing research agent.

Usage:
    python agent/run.py                          # Interactive mode
    python agent/run.py "suggest a cookie"       # Single query
    python agent/run.py --provider databricks    # Use Databricks
    python agent/run.py --auto-approve          # Skip confirmations
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from dotenv import load_dotenv

from agent.core import create_agent
from agent.config import AgentConfig


def setup_environment():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def run_interactive(agent, config: AgentConfig):
    """
    Run the agent in interactive mode.

    Args:
        agent: The deep agent instance
        config: Agent configuration
    """
    print("=" * 60)
    print("Marketing Research Agent")
    print("=" * 60)
    print(f"Provider: {config.provider}")
    print(f"Model: {config.model_name}")
    print("\nAsk me about product research! Type 'exit' or 'quit' to end.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nThanks for using Marketing Research Agent!")
                break

            if not user_input:
                continue

            # Invoke the agent
            print("\nAgent: ", end="", flush=True)
            result = agent.invoke({
                "messages": [{"role": "user", "content": user_input}]
            })

            # Extract and print the response
            if result and "messages" in result:
                response = result["messages"][-1]["content"]
                print(response)
            else:
                print("No response generated.")

            print()  # Empty line for readability

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            if config.verbose:
                import traceback
                traceback.print_exc()


def run_single_query(agent, query: str, config: AgentConfig):
    """
    Run a single query and exit.

    Args:
        agent: The deep agent instance
        query: The user query
        config: Agent configuration
    """
    try:
        result = agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })

        if result and "messages" in result:
            response = result["messages"][-1]["content"]
            print(response)
        else:
            print("No response generated.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if config.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Marketing Research Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with default provider (Anthropic)
  python agent/run.py

  # Single query
  python agent/run.py "suggest a summer cookie flavor"

  # Use Databricks provider
  python agent/run.py --provider databricks

  # Use OpenAI provider
  python agent/run.py --provider openai --model gpt-4-turbo

  # Use Databricks with custom model
  python agent/run.py \\
      --provider databricks \\
      --model databricks-meta-llama-3-1-405b-instruct

  # Auto-approve mode (no prompts)
  python agent/run.py --auto-approve "create a holiday cookie"
        """
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Single query to run (if omitted, runs in interactive mode)"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "databricks", "openai", "azure"],
        default="anthropic",
        help="Model provider to use (default: anthropic)"
    )
    parser.add_argument(
        "--model",
        help="Model name (provider-specific defaults if not specified)"
    )
    parser.add_argument(
        "--endpoint",
        help="Custom endpoint URL (required for Azure, optional for Databricks)"
    )
    parser.add_argument(
        "--workspace",
        help="Workspace directory for agent operations"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Automatically approve agent actions"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose logging (default: true)"
    )
    parser.add_argument(
        "--api-key",
        help="API key for the provider (or use environment variables)"
    )

    args = parser.parse_args()

    # Load environment
    setup_environment()

    # Create configuration
    try:
        config = AgentConfig(
            provider=args.provider,
            model_name=args.model,
            api_key=args.api_key,
            endpoint=args.endpoint,
            workspace_dir=args.workspace,
            auto_approve=args.auto_approve,
            verbose=args.verbose,
        )
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    # Create the agent
    try:
        print(f"Initializing Marketing Research Agent...")
        print(f"Provider: {config.provider}")
        print(f"Model: {config.model_name}")

        agent = create_agent(
            provider=config.provider,
            model_name=config.model_name,
            api_key=config.api_key,
            endpoint=config.endpoint,
            workspace_dir=config.workspace_dir,
            auto_approve=config.auto_approve,
        )

        print("Agent ready!\n")

    except Exception as e:
        print(f"Failed to create agent: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Run in appropriate mode
    if args.query:
        run_single_query(agent, args.query, config)
    else:
        run_interactive(agent, config)


if __name__ == "__main__":
    main()
