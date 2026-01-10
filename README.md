# Databricks OpenAI-Compatible API

A FastAPI application that provides an OpenAI-compatible chat completions endpoint for deployment on Databricks Apps.

## Features

- OpenAI-compatible `/api/v1/chat/completions` endpoint
- Simplified request/response models with Pydantic validation
- Health check endpoint at `/api/v1/healthcheck`
- Proper error handling with OpenAI-compatible error format
- Ready for Databricks Apps deployment

## Project Structure

```
├── app.py                          # Main FastAPI application
├── app.yaml                        # Databricks deployment config
├── requirements.txt                # Python dependencies
├── models/
│   ├── __init__.py
│   └── openai_schema.py           # OpenAI-compatible models
└── routes/
    ├── __init__.py
    └── v1/
        ├── __init__.py
        ├── completions.py         # Chat completions endpoint
        └── healthcheck.py         # Health check endpoint
```

## Local Development

### Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally

Start the development server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 5000
```

The API will be available at:
- API root: http://localhost:5000
- Interactive docs: http://localhost:5000/docs
- Health check: http://localhost:5000/api/v1/healthcheck
- Chat completions: http://localhost:5000/api/v1/chat/completions

### Testing the Endpoint

Using curl:
```bash
curl -X POST "http://localhost:5000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

Using Python:
```python
import requests

response = requests.post(
    "http://localhost:5000/api/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ]
    }
)

print(response.json())
```

## API Documentation

### POST /api/v1/chat/completions

Create a chat completion (OpenAI-compatible).

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "string"
    }
  ]
}
```

**Response:**
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response text..."
      },
      "finish_reason": "stop"
    }
  ]
}
```

**Error Response:**
```json
{
  "error": {
    "message": "Error description",
    "type": "invalid_request_error",
    "param": "messages",
    "code": "invalid_value"
  }
}
```

### GET /api/v1/healthcheck

Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-10T12:00:00.000000",
  "service": "openai-compatible-api"
}
```

## Databricks Deployment

1. Ensure all files are in your Databricks workspace
2. Deploy using Databricks Apps UI or CLI
3. The app.yaml configuration will use uvicorn to serve the FastAPI app
4. Access your app at the provided Databricks Apps URL

For detailed deployment instructions, see the [Databricks Apps documentation](https://docs.databricks.com/dev-tools/databricks-apps/).

## Current Limitations

- This is a dummy implementation - responses are static
- No actual model inference is performed
- Streaming is not supported
- Function calling/tools are not supported
- Request only accepts `messages` field
- Response only returns `id`, `object`, `created`, `choices` fields

## Future Enhancements

When ready to integrate real models:

1. **Add Model Integration:**
   - Connect to Databricks Model Serving endpoint
   - Or integrate with Databricks Foundation Model API
   - Or proxy to external OpenAI API

2. **Extend API Support:**
   - Add streaming support with SSE
   - Implement function/tool calling
   - Add more request parameters (temperature, max_tokens, etc.)
   - Include usage statistics in response

3. **Production Features:**
   - Add authentication/authorization
   - Implement rate limiting
   - Add comprehensive logging and monitoring
   - Set up proper error tracking

## References

- [Databricks FastAPI Getting Started](https://apps-cookbook.dev/docs/fastapi/getting_started/create/)
- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

This project is provided as-is for demonstration purposes.
