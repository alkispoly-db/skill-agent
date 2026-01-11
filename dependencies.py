"""
FastAPI dependency injection utilities.
"""
from fastapi import Request
from typing import Any


def get_agent(request: Request) -> Any:
    """
    Get the shared agent instance from application state.

    This dependency provides access to the agent initialized at app startup.

    Args:
        request: FastAPI request object

    Returns:
        The initialized agent instance

    Raises:
        RuntimeError: If agent is not initialized
    """
    if not hasattr(request.app.state, "agent"):
        raise RuntimeError(
            "Agent not initialized. Check application startup logs for errors."
        )

    return request.app.state.agent
