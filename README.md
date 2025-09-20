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

## Sample command: current working command for basic.py using tester_server.py with sample tools for tool description prompt injection attack:
    uv run run.py --transport stdio --suite basic --test tool_description_pinjection --cmd python --arg /home/alex/Desktop/projectCompliance/mcp-tester/tester_server.py

# Explanation of Current Modules
## generic_client.py
This file houses the MCPTesterClient Class, which is the primary client you use to connect to MCP servers. It is the primary client to be used by each test suite. The goal is for this class to act as a generic connector between multiple different MCP servers and can free have standard or custom tests plugged into the client.

This class provides methods to configure, connect, and manage multiple MCP server sessions using different transports (e.g., stdio, streamable HTTP/S). It is designed to work across different transports to avoid the difficulties testing through both local and third-party hosted MCP servers and tools. 

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

## run.py
This is the file that runs and begins the CLI tool. Read the docstring for the run.py file or the "How to use" steps at the beginning of this markdown in order to see how to use run.py.

## tester_server.py | adversarial_tools.py | sample_tools.py
This is a mock local server that can be connected to the generic MPC client to demonstrate basic server capabilities. The tester_server is connected through a local stdio transport and connects to both adversarial_tools.py and sample_tools.py as mock adversarial and mock sample tools to test proof of concept/generic form adversarial methods to fine-tune test sensitivity and accuracy. Please feel free to change this as you wish.

# How to add Tests and Servers
## How to add tests
To add tests, create a new {testname}.py file that holds your test functionality. Tests should take in any number of parameters and an MCPTesterClient object. The test should run by directly calling the functionality from or through the client as it should already be connected to the target servers upon executing run.py. See Sample Tests for examples.

In order to register the tests within run.py, create a globl dictionary that maps the test name to the callable: i.e. TESTSUITE_INDEX = {"testname": Callable[testname]}. Then, in run.py import the testsuite index and add it to the TEST_REGISTRY index. This is a very simple and not very scalable method of doing this. In order to be more scalable, the next person who works on this testing suite project is recommended to use python decorators as a wrapper to help wrap and register tests, instead of needing to add and change an internal TEST_REGISTRY every time a new suite is added. Hopefully, this method will be deprecated soon, I simply didn't have time to engineer a better solution given my looming end date. 

# Explanation of Sample Tests
## basic.py | Basic Tests:
1. tool_description_pinjection

This is a common type of attack that uses prompt/command injection using the tool descriptions. This is likely the most common case of MCP prompt injection attacks. MCP clients can potentially load a predefined list of the tools and their descriptions directly into the agent's system prompt on the client side as default behaviour. This is dangerous as it allows malicious actors access directly to the model system prompt through the modification of tool descriptions.

This test checks for any possible prompt injection scheme within the tool descriptions by loading every server connected with the generic client. It then calls the server.list_tools() method on each connected server. It uses a judge model to output a determination on the risk level of whether or not this prompt is attempting to inject malicious commands or instructions to the agent. This is done through the output in json format that gives a risk level (Low, Moderate, Severe) and a brief description back to the client.

Methods of improvement:
- Judge model: Currently Llama-3.1-8B-Instruct running locally,
This can be changed to a fined-tuned model that is better trained on types of adversarial commands.
- UI adjustment: 
Right now the output is just being printed to the stdout/terminal with no other forms of saving. If we'd like to turn this into production level code for other people to use, this should be connected to a database or some other form a data aggregation for better analyses and scalability.

2. tool_response_pinjection

This is the second most common type of attack against MCP servers using the tool responses. Depending how certain clients/agent handles responses, the responses from the MCP server tools can be used to inject malicious prompts or commands into the client operations. A simple example of such an attack is if the client uses an unprotected os.system() command to handle the response from the MCP tool. An unescaped string can easily cause greater security breaches. This test intends to provide a sample input to the parameters of the tools in a given MCP server and recieves the responses. It will then use a judge model to see whether or not the the response attempted command injections. 

Methods of Improvement:
- Non Implement Error: Use cases of tools too broad, unable to make a generic test for all types of tools with all different types of input needs. 

## advanced.py | Advanced Tests:
1. timeout_tester

This tests a standard form of the timeout resource leakage attack common in servers for only stdio transport connections. It looks at the child process that spawned the server through stdio transport through find_stdio_child() method and takes a snapshot before and after timeout disconnection.

Methods of Improvement:
- A lot of Bugs: didn't have time to fix them before m internship period was over and through my relative inexperience with networking. 