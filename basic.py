from typing import Dict, Callable
from generic_client import MCPTesterClient
import logging
from judge_model import JudgeModel
import asyncio

MODEL_PATH = "/home/alex/Desktop/projectCompliance/Llama-3.1-8B-Instruct-hf"

logger = logging.getLogger(__name__)

async def tool_description_pinjection(tester_client: MCPTesterClient, **kwargs) -> None:
    """
    Does a basic scan of the tool descriptions to ensure they do not contain
    prompt injection attacks.
    """
    server_ids = tester_client.server_params.keys()
    logger.info(f"Running tool description prompt injection test on servers {server_ids}")
    judge_model = JudgeModel(model_path=MODEL_PATH)

    for server_id in server_ids:
        logger.info(f"Testing server {server_id}")
        # Implement the scan logic here
        tool_results = await tester_client.sessions[server_id].list_tools()
        tool_list = tool_results.tools  # Assuming the result has a "tools" key with a list of tools
        for tool in tool_list:
            logger.info(f"Evaluating tool {tool.name}")
            tool_description = tool.description
            if not tool_description:
                logger.warning(f"Tool {tool.name} has no description")
            response = judge_model.judge(tool_description)
            judgement = judge_model.parse_judgement(response)
            logger.info(f"Tool {tool.name} judged as {judgement}")

            if judgement.get("risk_level") == "Strong":
                logger.warning(f"Tool {tool.name} has a strong risk level.")
            elif judgement.get("risk_level") == "Moderate":
                logger.warning(f"Tool {tool.name} has a moderate risk level.")
            elif judgement.get("risk_level") == "Low":
                logger.info(f"Tool {tool.name} has a low risk level.")
    return

async def tool_response_pinjection(tester_client: MCPTesterClient, **kwargs) -> None:
    """
    Does a basic scan of the tool responses to ensure they do not contain
    prompt or command injection attacks.
    """
    server_ids = tester_client.server_params.keys()
    logger.info(f"Running tool response prompt injection test on servers {server_ids}")

    for server_id in server_ids:
        logger.info(f"Testing server {server_id}")
    raise NotImplementedError("tool_response_pinjection is not implemented yet")

BASIC_TEST_REGISTRY: Dict[str, Callable] = {
    "tool_description_pinjection": tool_description_pinjection,
    "tool_response_pinjection": tool_response_pinjection,
}