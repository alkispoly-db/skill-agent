# Example of a skills-based agent

This app shows how to build an agent entirely based on skills and a system prompt. The agent is deployed as a databricks app and exposes an 
OpenAI-compatible chat/completions endpoint.

## Project Structure

```
├── app.py                          # Main FastAPI application
├── app.yaml                        # Databricks deployment config
├── config.py                       # Configuration with Pydantic settings
├── dependencies.py                 # FastAPI dependency injection
├── requirements.txt                # Python dependencies
├── chat_cli.py                     # Interactive CLI client for testing
├── agent/
│   ├── __init__.py
│   ├── core.py                    # Agent creation and initialization
│   ├── provider.py                # Multi-provider support (Databricks, Anthropic, etc.)
│   ├── system_prompt.md           # Agent system prompt (editable)
│   └── skills/
│       └── cookie-flavor-generator/  # Example skill
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

Using chat_cli.py (interactive client with conversation history):
```bash
python chat_cli.py --host localhost --port 5000
```

This provides an interactive chat interface where you can have multi-turn conversations with the agent.

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

### Quick Start

**Prerequisites**: Databricks CLI configured with a profile (assumes `~/.databrickscfg` is already set up)

```bash
# 1. Create the app
databricks apps create skill-agent --description "Marketing Research Agent"

# 2. Upload source code
databricks workspace import-dir . /Workspace/Users/YOUR.EMAIL@company.com/apps/skill-agent --overwrite

# 3. Deploy
databricks apps deploy skill-agent --source-code-path /Workspace/Users/YOUR.EMAIL@company.com/apps/skill-agent

# 4. Test with chat_cli.py
python chat_cli.py --url $(databricks apps get skill-agent --output json | jq -r '.url') --databricks-profile DEFAULT
```

### Detailed Instructions

For comprehensive deployment instructions, troubleshooting, and monitoring, see **[DATABRICKS_DEPLOYMENT.md](./DATABRICKS_DEPLOYMENT.md)**.

## References

- [Databricks FastAPI Getting Started](https://apps-cookbook.dev/docs/fastapi/getting_started/create/)
- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

This project is provided as-is for demonstration purposes.
