import asyncio
import json
import logging
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re
from datetime import datetime
import os
from requests import session
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from contextlib import AsyncExitStack

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.types import Tool, CallToolResult, ListToolsResult, TextContent
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.client.stdio import stdio_client
except ImportError:
    print("MCP library not installed. Install with: pip install mcp")
    sys.exit(1)

class MCPTesterClient:
    """
    A client for managing and testing Model Context Protocol (MCP) servers. It is the primary client to be used by each test suite

    This class provides methods to configure, connect, and manage multiple MCP server sessions
    using different transports (e.g., stdio, streamable HTTP/S). It is designed to facilitate
    automated security and compliance testing of MCP-compatible servers.

    Key Features:
    - Add and store multiple server configurations (stdio, streamable_http, etc.)
    - Establish and manage asynchronous connections to MCP servers
    - Maintain active sessions and handle resource cleanup
    - Provide a unified interface for test suites to interact with MCP servers

    Attributes:
        transport (str): The default transport type for new servers (optional).
        server_params (Dict[str, Dict[str, Any]]): Mapping of server_id to server configuration dicts.
        sessions (Dict[str, ClientSession]): Active MCP client sessions by server_id.
        exit_stacks (Dict[str, AsyncExitStack]): Async context managers for resource cleanup per server.
        logger (logging.Logger): Logger for client events and errors.

    Example usage:
        client = MCPTesterClient(transport="stdio")
        client.add_server("local_server", {"transport": "stdio", "server_params": StdioServerParameters(...)})
        await client.connect_server_stdio("local_server", ...)
        # ... run tests ...
        await client.cleanup()
    """

    def __init__(self, transport = None):
    
        self.transport = transport
        self.logger = logging.getLogger(__name__)

        # server params are a dictionary of key server_id to the va lue of dictionary for the parameters
        #Parameters should be input in the form {"server_id": {<server parameters>}}
        #Parameter values should specify transport type and resulting value
            #Example: {"server1": {"transport": "stdio", "server_params": "StdioServerParameters(...)"}}
            #Example: {"server2": {"transport": "streamable_https", "server_url": "http://example.com/mcp"}}
        self.server_params = {}

        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stacks: Dict[str, AsyncExitStack] = {}

    def add_server(self, server_id: str, server_params: Dict[str, Any]):
        """
        Add a new server configuration.
        Input: 
            server_id as a string
            server_params as a dictionary of {"transport": transport, either "server_params" or "server_url" depending on transport type
        """
        self.logger.info(f"Adding server {server_id} with params {server_params}")
        self.server_params[server_id] = server_params

    async def connect_server_stdio(self, server_id: str, server_params: StdioServerParameters) -> Optional[ClientSession]:
            """Connect to an MCP server through stdio."""

            exit_stack = AsyncExitStack()
            self.exit_stacks[server_id] = exit_stack    

            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
            self.sessions[server_id] = session

            # Initialize the session - this performs the MCP handshake
            try:
                self.logger.info(f"Initializing session for stdio server {server_id}")
                await asyncio.wait_for(self.sessions[server_id].initialize(), timeout=5.0)
            except TimeoutError:
                exit_stack.aclose()
                self.sessions.pop(server_id, None)
                self.logger.error(f"Timeout while initializing session for server {server_id}")
                return None

            return session


    async def connect_server_streamable_https(self, server_id: str, server_url: str) -> Optional[ClientSession]:
        """Connect to an MCP server based on its configuration."""

        exit_stack = AsyncExitStack()
        self.exit_stacks[server_id] = exit_stack

        streams_context = streamablehttp_client(url=server_url)
        streams = await exit_stack.enter_async_context(streams_context)
        session = await exit_stack.enter_async_context(ClientSession(*streams))
        self.sessions[server_id] = session

        try:
            self.logger.info(f"Initializing session for streamable https server {server_id}")
            await asyncio.wait_for(self.sessions[server_id].initialize(), timeout=5.0)
        except TimeoutError:
            exit_stack.aclose()
            self.sessions.pop(server_id, None)
            self.logger.error(f"Timeout while initializing session for server {server_id}")
            return None

        return session
    
    async def cleanup(self):
        """Properly close all MCP connections and clean up resources."""
        self.logger.info("Cleaning up MCP client connections...")
        
        # Close all exit stacks (this will close sessions and processes)
        for server_id, exit_stack in self.exit_stacks.items():
            try:
                self.logger.info(f"Closing connection to {server_id}")
                await exit_stack.aclose()
            except Exception as e:
                self.logger.warning(f"Error closing {server_id}: {e}")
                continue
        # Clear the dictionaries
        self.sessions.clear()
        self.exit_stacks.clear()
        
        self.logger.info("✅ All connections cleaned up")




