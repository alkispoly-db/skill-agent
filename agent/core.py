"""
Core agent initialization and configuration with multi-provider support.
"""
from pathlib import Path
from typing import Optional

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from agent.provider import get_llm_from_provider


def get_skills_directory() -> str:
    """Get the absolute path to the skills directory."""
    current_dir = Path(__file__).parent
    skills_dir = current_dir / "skills"
    return str(skills_dir.absolute())


def create_agent(
    provider: str = "anthropic",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    workspace_dir: Optional[str] = None,
    auto_approve: bool = False,
    **provider_kwargs
):
    """
    Create a deep agent with skills for marketing team product research.

    The agent has access to multiple skills including cookie flavor generation
    and can be extended with additional skills as needed.

    Supports multiple model providers: Anthropic, Databricks, OpenAI, Azure.

    Args:
        provider: Model provider (anthropic, databricks, openai, azure)
        model_name: Model identifier (provider-specific defaults if None)
        api_key: API key for the provider
        endpoint: Custom endpoint (required for Databricks, Azure)
        workspace_dir: Directory for agent file operations
        auto_approve: If True, automatically approve agent actions
        **provider_kwargs: Additional provider-specific parameters

    Returns:
        Configured deep agent instance
    """
    # Set provider-specific default models if not specified
    if model_name is None:
        defaults = {
            "anthropic": "claude-sonnet-4-5-20250929",
            "databricks": "databricks-claude-sonnet-4-5",
            "openai": "gpt-4-turbo",
            "azure": "gpt-4",
        }
        model_name = defaults.get(provider)

    # Set up workspace directory
    if workspace_dir is None:
        workspace_dir = str(Path.cwd() / "workspace")

    workspace_path = Path(workspace_dir)
    workspace_path.mkdir(exist_ok=True)

    # Get skills directory
    skills_dir = get_skills_directory()

    # Create LLM instance based on provider
    llm = get_llm_from_provider(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        endpoint=endpoint,
        **provider_kwargs
    )

    # System prompt for marketing team product research agent
    system_prompt = """You are a product research assistant helping the marketing team with various research tasks.

Your role is to assist with:
- Product ideation and concept development
- Market research and competitive analysis
- Creative product naming and positioning
- Consumer insights and trend analysis
- Product feature exploration

You have access to specialized skills including cookie flavor generation, which you should use
when relevant to product development tasks. Apply your knowledge thoughtfully and provide
actionable insights that help the marketing team make informed decisions.

When working on product research:
- Consider market trends and consumer preferences
- Think about competitive positioning
- Evaluate feasibility and practical execution
- Provide creative yet realistic recommendations
- Support your suggestions with reasoning

Be professional, analytical, and creative in your responses."""

    # Configure interrupt behavior
    interrupt_on = [] if auto_approve else ["task"]

    # Create the agent with skills
    agent = create_deep_agent(
        model=llm,
        system_prompt=system_prompt,
        skills=[skills_dir],
        backend=FilesystemBackend(
            root_dir=str(workspace_path),
            virtual_mode=True
        ),
        interrupt_on=interrupt_on,
        name="marketing-research-agent",
    )

    return agent
