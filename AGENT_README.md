# Marketing Research Agent - Implementation Complete

A deep agent system using deepagents library with multi-provider support for marketing team product research.

The agent has access to multiple skills including cookie flavor generation and can be extended with additional skills as needed.

## What Has Been Implemented

### ✅ Core Files
- `agent/config.py` - Agent-specific Pydantic configuration
- `agent/core.py` - Agent initialization with provider-specific LLM creation
- `agent/provider.py` - Multi-provider LLM support
- `agent/system_prompt.md` - System prompt (easy to edit)
- `agent/__init__.py` - Package initialization
- `chat_cli.py` - Interactive HTTP client for testing the agent via API
- `config.py` - Main application configuration
- `app.py` - FastAPI application with agent integration

### ✅ Skills
- `agent/skills/cookie-flavor-generator/SKILL.md` - Comprehensive skill definition
- `agent/skills/cookie-flavor-generator/references/flavor-profiles.md` - Flavor pairing reference

### ✅ Configuration
- `requirements.txt` - Updated with deepagents and provider dependencies
- `.env.example` - Multi-provider configuration template

### ✅ Project Structure
```
Project Root/
├── app.py                      # FastAPI application with agent
├── config.py                   # Main application configuration
├── chat_cli.py                 # Interactive HTTP client
├── dependencies.py             # FastAPI dependency injection
├── routes/
│   └── v1/
│       ├── completions.py      # OpenAI-compatible chat endpoint
│       └── healthcheck.py      # Health check endpoint
├── models/
│   └── openai_schema.py        # Pydantic models
└── agent/
    ├── __init__.py
    ├── config.py               # Agent-specific configuration
    ├── core.py                 # Agent creation and initialization
    ├── provider.py             # Multi-provider LLM support
    ├── system_prompt.md        # System prompt (easy to edit)
    └── skills/
        └── cookie-flavor-generator/
            ├── SKILL.md
            └── references/
                └── flavor-profiles.md
```

## Supported Providers

### 1. Databricks (Default: `databricks-claude-sonnet-4-5`)
- Uses Databricks SDK for authentication
- Supports Foundation Model API and Model Serving endpoints
- Available models:
  - `databricks-claude-sonnet-4-5` (default)
  - `databricks-meta-llama-3-1-405b-instruct`
  - `databricks-meta-llama-3-1-70b-instruct`
  - `databricks-meta-llama-3-1-8b-instruct`
  - `databricks-dbrx-instruct`
  - `databricks-mixtral-8x7b-instruct`

### 2. Anthropic (Default: `claude-sonnet-4-5-20250929`)
- Direct Claude API integration
- Requires ANTHROPIC_API_KEY

### 3. OpenAI (Default: `gpt-4-turbo`)
- OpenAI API integration
- Requires OPENAI_API_KEY

### 4. Azure (Default: `gpt-4`)
- Azure OpenAI integration
- Requires AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd /home/alkis.polyzotis/skill-agent
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Provider

#### For Databricks (Recommended):
```bash
# Configure Databricks SDK
databricks configure --token

# Or set environment variables
export DATABRICKS_HOST="https://your-workspace.databricks.com"
export DATABRICKS_TOKEN="your-token"
```

#### For Anthropic:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

#### For OpenAI:
```bash
export OPENAI_API_KEY="your-api-key"
```

#### For Azure:
```bash
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
```

### Step 3: Run the Application

#### Start the FastAPI Server:
```bash
# The server uses configuration from .env or environment variables
uvicorn app:app --host 0.0.0.0 --port 5000
```

#### Test with the Interactive Client:
```bash
# In another terminal, run the chat client
python chat_cli.py                    # Connect to localhost:5000
python chat_cli.py --port 8000        # Custom port
python chat_cli.py --host 192.168.1.100  # Remote host
```

#### Configure Provider (via .env or environment):
```bash
# Set in .env file or environment variables
export AGENT_PROVIDER=databricks           # or anthropic, openai, azure
export AGENT_MODEL=databricks-claude-sonnet-4-5
export DATABRICKS_PROFILE=DEFAULT          # For Databricks CLI auth
```

## Usage Examples

### Example 1: Interactive Chat Mode
```bash
# Terminal 1: Start the server
$ uvicorn app:app --host 0.0.0.0 --port 5000

# Terminal 2: Run the chat client
$ python chat_cli.py

Connecting to http://localhost:5000...
Connection successful!

============================================================
Marketing Research Agent - Interactive Client
============================================================
Connected to: http://localhost:5000

Ask me about product research! Type 'exit' or 'quit' to end.
Type 'clear' to reset conversation history.

You: Suggest a cookie for Valentine's Day

Agent: [Creative cookie flavor suggestion with description]

You: What about a summer flavor?

Agent: [Summer cookie suggestion - remembers conversation context]
```

### Example 2: API Usage with curl
```bash
curl -X POST "http://localhost:5000/api/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Suggest a unique cookie flavor"}
    ]
  }'
```

### Example 3: Python API Client
```python
import requests

response = requests.post(
    "http://localhost:5000/api/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "What cookie pairs well with coffee?"}
        ]
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

## Testing the Agent

### Quick Verification Test

1. **Check skills are loaded:**
```bash
ls -la agent/skills/cookie-flavor-generator/
# Should show SKILL.md and references/
```

2. **Verify configuration:**
```bash
python -c "from agent.config import AgentConfig; c = AgentConfig(provider='databricks'); print(f'Model: {c.model_name}')"
# Should output: Model: databricks-claude-sonnet-4-5
```

3. **Test agent creation (without invoking):**
```python
from agent import create_agent

# This will verify imports and basic setup
agent = create_agent(provider="databricks", auto_approve=True)
print("Agent created successfully!")
```

### Test Queries

Try these queries to test the skill:
1. "Suggest a chocolate chip cookie variation"
2. "Create a cookie for a summer barbecue"
3. "What would pair well with lemon and lavender?"
4. "Design a cookie inspired by tiramisu"
5. "Give me a gluten-free cookie idea"

## Architecture Highlights

### Multi-Provider Support
- Provider-agnostic design
- Automatic credential management for Databricks via SDK
- Provider-specific default models
- Easy to extend with new providers

### Skills System
- Progressive disclosure pattern
- SKILL.md format for skill definition
- Reference materials for deep knowledge
- Filesystem-based skill loading

### Agent Features
- Interactive REPL mode
- Single-query mode for scripting
- Auto-approve mode for automation
- Comprehensive error handling
- Verbose logging for debugging

## Architecture

### FastAPI Integration

The agent is fully integrated with the FastAPI application:

```python
# app.py - Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize agent at startup
    agent = create_agent(
        provider=config.agent_provider,
        model_name=config.agent_model,
        auto_approve=True
    )
    app.state.agent = agent  # Shared instance
    yield
    # Cleanup on shutdown

# routes/v1/completions.py - OpenAI-compatible endpoint
@router.post("/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    agent = Depends(get_agent)  # Dependency injection
):
    # Convert OpenAI messages to agent format
    agent_messages = convert_openai_to_agent_messages(request.messages)

    # Invoke agent
    result = agent.invoke({"messages": agent_messages})

    # Return OpenAI-compatible response
    return ChatCompletionResponse(...)
```

**Key Features:**
- Single shared agent instance (efficient)
- Dependency injection via FastAPI
- OpenAI-compatible API format
- Lifespan management for startup/shutdown

## Next Steps

1. **Extend skills:**
   - Add more skills for market research and competitive analysis
   - Create custom skills for specific product development use cases
   - Add skills for consumer insights and trend analysis

2. **Add tests:**
   - Create unit tests for configuration
   - Add integration tests with mock LLMs
   - Test skill loading and formatting
   - End-to-end API tests

3. **Enhance features:**
   - Add streaming support for real-time responses
   - Implement session-based conversation persistence
   - Add usage tracking and analytics
   - Support for file uploads and document analysis

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Databricks Authentication
```bash
# Reconfigure Databricks SDK
databricks configure --token
```

### Skill Not Found
```bash
# Verify skills directory exists
ls -la agent/skills/cookie-flavor-generator/SKILL.md
```

### Provider Errors
```bash
# Check environment variables
env | grep -E "(DATABRICKS|ANTHROPIC|OPENAI|AZURE)"
```

## Implementation Complete! 🎉

The marketing research agent is fully implemented and integrated with:
- ✅ Multi-provider support (Databricks, Anthropic, OpenAI, Azure)
- ✅ Databricks CLI profile authentication
- ✅ FastAPI integration with OpenAI-compatible API
- ✅ Interactive HTTP chat client (chat_cli.py)
- ✅ Cookie flavor generation skill
- ✅ System prompt in editable markdown file
- ✅ Lifespan management and dependency injection
- ✅ Code simplification and clean architecture
- ✅ Production-ready configuration

Ready to assist with product research and development!
