#!/usr/bin/env python3
"""
MCP Safety Tester CLI Tool
===========================

A command-line interface for testing MCP (Model Context Protocol) servers for security vulnerabilities.
This tool allows you to connect to MCP servers and run security test suites against them.

Usage:
    # Run basic security test suite against a stdio server
    python run.py --server-id tester_server --transport stdio --suite basic --cmd python --arg tester_server.py
    
    # Run a specific test from the basic suite
    python run.py --server-id tester_server --transport stdio --suite basic --test tool_description_pinjection --cmd python --arg tester_server.py
    
    # Run advanced test suite against an HTTP server
    python run.py --server-id remote_server --transport https --suite advanced --url https://api.example.com/mcp
    
    # Get help
    python run.py --help

    # CURRENT WORKING COMMAND FOR BASIC.PY USING LOCAL_SERVER.PY FROM INIT_PROTO:
    uv run run.py --transport stdio --suite basic --test tool_description_pinjection --cmd python --arg /home/alex/Desktop/projectCompliance/MCPsponge/init_proto/local_server.py
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from basic import BASIC_TEST_REGISTRY
from advanced import ADVANCED_TEST_REGISTRY

# Add the current directory to Python path to import local modules
sys.path.append(str(Path(__file__).parent))

from generic_client import MCPTesterClient
from mcp import StdioServerParameters

TEST_REGISTRY = {
    "basic": BASIC_TEST_REGISTRY,
    "advanced": ADVANCED_TEST_REGISTRY,
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    # Create a parent parser with shared arguments
    shared_parser = argparse.ArgumentParser(
        description="MCP Safety Tester CLI - Test Model Context Protocol servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
  # Run basic test suite for a local server
  python run.py --server-id 1 --transport stdio --suite basic'
        """,
        add_help=False)
    shared_parser.add_argument("--server-id", type=str, default="1", help="ID of the server to connect to")
    shared_parser.add_argument("--transport", choices=["stdio", "https"], required=True, help="Transport method to use")

    # This will change once we add more test suites
    shared_parser.add_argument("--suite", default="basic", choices=["basic","advanced"], required=True, help="Name of testing suite to use")
    shared_parser.add_argument("--test", default=None, help="Specific test in suite to run, if not run all")

    g_stdio = shared_parser.add_argument_group("stdio transport")
    g_stdio.add_argument("--cmd")
    g_stdio.add_argument("--arg", action="append")
    g_stdio.add_argument("--cwd")
    g_stdio.add_argument("--env", action="append",
                         help="KEY=ENV:VARNAME (repeatable)")

    g_http = shared_parser.add_argument_group("streamable HTTP transport")
    g_http.add_argument("--url")
    g_http.add_argument("--header", action="append",
                        help="Name=ENV:VARNAME (repeatable)")

    return shared_parser

async def run_tests(tester_client: MCPTesterClient, server_id: str, suite: str, test: Optional[str], test_kwargs: Dict[str, Any]) -> Any:
        try:
            test_registry = TEST_REGISTRY.get(suite)
            common_kwargs = {
                "server_id": server_id
                }
            if test:
                if test in test_registry:
                    tool_func = test_registry[test]
                    logger.info(f"Running specific test '{test}' from suite '{suite}'")
                    await tool_func(tester_client, **common_kwargs)
                else:
                    logger.error(f"Test '{test}' not found in suite '{suite}'")
                    sys.exit(1)
            else:
                logger.info(f"Running all tests from suite '{suite}'")
                for test_name, tool_func in test_registry.items():
                    await tool_func(tester_client, **common_kwargs)
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            sys.exit(1)

async def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()

    server_id = args.server_id
    transport = args.transport
    suite = args.suite
    test = args.test
    logger.info(f"Starting MCP Tester with server_id={server_id}, transport={transport}")

    tester_client = None

    try:
        if transport == "stdio":
            logger.info("Creating MCPTesterClient with stdio transport")
            tester_client = MCPTesterClient(transport="stdio")

            logger.info(f"Adding server configuration... command: {args.cmd}, args: {args.arg}, cwd: {args.cwd}, env: {args.env}")
            tester_client.add_server(server_id, {
                "transport": "stdio",
                "server_params": StdioServerParameters(
                    command=args.cmd,
                    args=args.arg if args.arg else [],
                    cwd=args.cwd,
                    env=dict(env.split('=', 1) for env in args.env) if args.env else None
                )
            })
            await tester_client.connect_server_stdio(server_id, tester_client.server_params[server_id]["server_params"])
        elif transport == "http":
            tester_client = MCPTesterClient(transport="https")
            tester_client.add_server(server_id, {
                "transport": "streamable_https",
                "server_url": args.url,
                "headers": dict(header.split('=', 1) for header in args.header) if args.header else None
            })
            await tester_client.connect_server_streamable_https(server_id, args.url)
        else:
            raise ValueError(f"Unsupported transport: {transport}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

    if tester_client is None or server_id not in tester_client.sessions:
        logger.error("Failed to create or connect MCPTesterClient.")
        sys.exit(1)

    try:
        await run_tests(tester_client, server_id, suite, test, args)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        if tester_client:
            try:
                # Close all exit stacks properly
                for exit_stack in tester_client.exit_stacks.values():
                    await exit_stack.aclose()
                logger.info("🧹 Cleaned up MCP connections")
            except Exception as cleanup_error:
                logger.warning(f"Error during cleanup: {cleanup_error}")


if __name__ == "__main__":
    asyncio.run(main())
