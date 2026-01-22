import pytest
from agent.agent import root_agent


@pytest.mark.asyncio
async def test_root_agent_responds():
    """Test that root agent returns a response."""
    result = await root_agent("help me prepare content for Linear algebra")
    assert result is not None


# @pytest.mark.asyncio
# async def test_root_agent_with_text():
#     """Test root agent with text input."""
#     result = await root_agent("Hello, agent!")
#     assert result is not None