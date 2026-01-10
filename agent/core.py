"""
Core agent initialization and configuration with multi-provider support.
"""
import os
from pathlib import Path
from typing import Optional

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend


def get_skills_directory() -> str:
    """Get the absolute path to the skills directory."""
    current_dir = Path(__file__).parent
    skills_dir = current_dir / "skills"
    return str(skills_dir.absolute())


def get_llm_from_provider(
    provider: str,
    model_name: str,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    **kwargs
):
    """
    Get LLM instance based on provider.

    Supported providers:
    - anthropic: Claude models via Anthropic API
    - databricks: Models via Databricks Foundation Model API or Model Serving
    - openai: OpenAI models
    - azure: Azure OpenAI models

    Args:
        provider: Provider name (anthropic, databricks, openai, azure)
        model_name: Model identifier
        api_key: API key (provider-specific)
        endpoint: Custom endpoint URL (for Databricks, Azure)
        **kwargs: Additional provider-specific parameters

    Returns:
        LangChain LLM instance
    """
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        return ChatAnthropic(
            model=model_name,
            api_key=api_key,
            **kwargs
        )

    elif provider == "databricks":
        from langchain_community.chat_models import ChatDatabricks

        # Databricks uses SDK for authentication - no need to pass api_key explicitly
        # SDK will automatically use ~/.databrickscfg or environment variables

        return ChatDatabricks(
            endpoint=endpoint or "databricks",
            model=model_name,
            **kwargs
        )

    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            **kwargs
        )

    elif provider == "azure":
        from langchain_openai import AzureChatOpenAI

        if api_key is None:
            api_key = os.getenv("AZURE_OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "Azure OpenAI API key required. Set AZURE_OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        if not endpoint:
            raise ValueError(
                "Azure OpenAI endpoint required. Set AZURE_OPENAI_ENDPOINT environment variable "
                "or pass endpoint parameter."
            )

        return AzureChatOpenAI(
            azure_endpoint=endpoint,
            deployment_name=model_name,
            api_key=api_key,
            api_version="2024-02-15-preview",
            **kwargs
        )

    else:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: anthropic, databricks, openai, azure"
        )


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
