import pytest
from unittest.mock import patch

from src.graph.nodes import researcher_node
from src.graph.types import State
from src.prompts.planner_model import Plan, Step, StepType
from langgraph.types import Command


@pytest.mark.asyncio
async def test_researcher_node_includes_law_lookup():
    step = Step(
        need_web_search=False,
        title="test",
        description="desc",
        step_type=StepType.RESEARCH,
    )
    plan = Plan(
        locale="en-US",
        has_enough_context=True,
        thought="",
        title="",
        steps=[step],
    )
    state = State(messages=[], current_plan=plan)
    captured_tools = []

    async def fake_execute(state, agent, agent_type):
        return Command(update={}, goto="research_team")

    def fake_create_agent(agent_name, agent_type, tools, prompt_template):
        captured_tools.extend(tools)

        class DummyAgent:
            async def ainvoke(self, input, config):
                return {"messages": [{"content": ""}]}

        return DummyAgent()

    with patch("src.graph.nodes.create_agent", side_effect=fake_create_agent), patch(
        "src.graph.nodes._execute_agent_step", side_effect=fake_execute
    ):
        await researcher_node(state, {"configurable": {}})

    tool_names = {
        getattr(tool, "name", getattr(tool, "__name__", "")) for tool in captured_tools
    }
    assert "law_lookup" in tool_names
