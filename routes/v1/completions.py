"""
Chat completions endpoint - OpenAI-compatible API.
"""

import uuid
import time
from fastapi import APIRouter, HTTPException, status
from models.openai_schema import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ResponseMessage,
    ErrorResponse,
)

router = APIRouter()


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
)
async def create_chat_completion(request: ChatCompletionRequest):
    """
    Create a chat completion (OpenAI-compatible endpoint).

    This is a dummy implementation that returns realistic but static responses.
    No actual model inference is performed.

    Args:
        request: Chat completion request with messages

    Returns:
        ChatCompletionResponse with dummy content

    Raises:
        HTTPException: 400 if messages array is empty
        HTTPException: 500 for unexpected errors
    """
    try:
        # Validate request
        if not request.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "message": "messages array cannot be empty",
                        "type": "invalid_request_error",
                        "param": "messages",
                        "code": "invalid_value",
                    }
                },
            )

        # Get last message to generate dummy response
        last_message = request.messages[-1]

        # Generate dummy content
        if last_message.content:
            content_preview = last_message.content[:50]
            if len(last_message.content) > 50:
                content_preview += "..."
            dummy_content = f"This is a dummy response to: {content_preview}"
        else:
            dummy_content = "This is a dummy response to your message."

        # Generate unique completion ID
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"

        # Create response
        response = ChatCompletionResponse(
            id=completion_id,
            object="chat.completion",
            created=int(time.time()),
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ResponseMessage(role="assistant", content=dummy_content),
                    finish_reason="stop",
                )
            ],
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "message": str(e),
                    "type": "internal_error",
                    "code": "server_error",
                }
            },
        )
