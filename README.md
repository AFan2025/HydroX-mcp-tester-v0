# HydroX-mcp-tester-v0
MCP Unified Safety Tester CLI for HydroX AI. Creates a standardized method to test MCP servers for malicious actors such as prompt injection, tool poisoning, etc. 

# Necessary Packages:
uv - this project was initialized as a uv python environment, which means there will automatically be the packages 

# How to use:
## Step 1: run.py
This is the primary python file to run to use as the python CLI tool. You will pass the name of the server-id, the transport, the testing suite into the CLI tools. Each transport as its own CLI arguments that you need to fill out.

### Run basic security test suite against a stdio server 
    python run.py --server-id tester_server --transport stdio --suite basic --cmd python --arg tester_server.py

### Run a specific test from the basic suite
    python run.py --server-id tester_server --transport stdio --suite basic --test tool_description_pinjection --cmd python --arg tester_server.py

## Run advanced test suite against an HTTP server
    python run.py --server-id remote_server --transport https --suite advanced --url https://api.example.com/mcp

## Best Run for current tool set:
## CURRENT WORKING COMMAND FOR BASIC.PY USING TESTER_SERVER.PY WITH SAMPLE TOOLS:
    uv run run.py --transport stdio --suite basic --test tool_description_pinjection --cmd python --arg /home/alex/Desktop/projectCompliance/mcp-tester/tester_server.py