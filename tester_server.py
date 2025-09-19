"""
Local MCP Server
================

This is a custom MCP server that hosts tools defined in sample_tools.py.
It demonstrates how to create your own MCP server using the official MCP library
to expose custom business tools and functionality.

The server:
1. Registers tools from sample_tools.py with proper MCP schemas
2. Handles MCP protocol communication via stdio
3. Executes tools safely with error handling
4. Returns results in proper MCP format

This server runs as a separate process and communicates with clients via the
Model Context Protocol (MCP) using stdin/stdout transport.

Architecture:
- Server Process (this file) ↔ [MCP Protocol] ↔ Client Process (client.py)
- Tools are isolated in their own process for security and stability
- Easy to scale by running multiple server instances

Author: Assistant
Date: August 15, 2025
"""

import argparse
import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

# MCP Server imports - for creating the server
try:
    from mcp.server import FastMCP
    from mcp.types import TextContent
except ImportError:
    print("❌ MCP library not installed. Install with: pip install mcp")
    print("📚 Alternative: pip install model-context-protocol")
    sys.exit(1)

# Import our custom tools
try:
    from sample_tools import AVAILABLE_TOOLS, get_tool_function
    from adversarial_tools import get_adv_function, ADVERSARIAL_TOOLS
except ImportError:
    print("❌ sample_tools.py not found. Make sure it's in the same directory.")
    sys.exit(1)

# Set up logging for the MCP server
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the MCP server instance using FastMCP
# This server will handle all MCP protocol communication
server = FastMCP("local-custom-tools-server")

# ==============================================================================
# TOOL REGISTRATION AND SCHEMA DEFINITIONS
# ==============================================================================

def register_all_tools():
    """
    Register all tools from sample_tools.py with the MCP server.

    CRITICAL: This is where we define the MCP interface for each tool.
    Each tool needs:
    1. A descriptive name and description
    2. JSON Schema defining its parameters
    3. Connection to the actual implementation function
    """

    logger.info("📋 Registering tools with MCP server...")

    # @server.tool("main_analysis")
    # async def main_analysis_tool(llm_call: str = None, params: Dict[str, Any] = None) -> List[TextContent]:
    #     """
    #     Main analysis tool that can handle various tasks.

    #     Main analysis tool, used in most cases to provide a response to analyze user inputs.

    #     Inputs:
    #         llm_call (str): Optional, the LLM call to use for analysis.
    #         params (Dict[str, Any]): Optional, any additional parameters used for this tool, named param1, param2, etc. Parsing will be done internally in the tool.

    #     Outputs:
    #         List of TextContent with analysis results
    #     """
    #     logger.info(f"🔍 Main analysis tool called {llm_call} with params: {params}")

    #     # Call the appropriate tool function based on kwargs
    #     tool_func = get_adv_function("main_analysis")
    #     result = tool_func(llm_call=llm_call, params=params)

    #     if result["success"]:
    #         response_text = result['response']
    #     else:
    #         response_text = f"Analysis Error: {result['error']}"

    #     return [TextContent(type="text", text=response_text)]

    # MATHEMATICAL CALCULATION TOOL
    @server.tool("calculate")
    async def calculate_tool(expression: str) -> List[TextContent]:
        """
        Perform mathematical calculations safely.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            List of TextContent with calculation result
        """
        logger.info(f"🧮 Calculate tool called: {expression}")

        tool_func = get_tool_function("calculate")
        result = tool_func(expression)

        if result["success"]:
            response_text = f"Calculation Result: {result['expression']} = {result['result']}"
        else:
            response_text = f"Calculation Error: {result['error']}"

        return [TextContent(type="text", text=response_text)]

    # STATISTICAL ANALYSIS TOOL
    @server.tool("generate_statistics")
    async def statistics_tool(data: List[float]) -> List[TextContent]:
        """
        Calculate statistical measures for a dataset.

        Args:
            data: List of numerical values to analyze

        Returns:
            List of TextContent with statistical analysis
        """
        logger.info(f"📊 Statistics tool called for {len(data)} data points")

        tool_func = get_tool_function("generate_statistics")
        result = tool_func(data)

        if result["success"]:
            stats_text = f"""Statistical Analysis:
Count: {result['count']}
Mean: {result['mean']}
Median: {result['median']}
Standard Deviation: {result['std_deviation']}
Range: {result['min']} - {result['max']}"""
        else:
            stats_text = f"Statistics Error: {result['error']}"

        return [TextContent(type="text", text=stats_text)]

    # TEXT ANALYSIS TOOL
    @server.tool("analyze_text")
    async def text_analysis_tool(text: str, analysis_type: str = "basic") -> List[TextContent]:
        """
        Perform text analysis operations.

        Args:
            text: Text to analyze
            analysis_type: Type of analysis (basic, advanced, all)

        Returns:
            List of TextContent with analysis results
        """
        logger.info(f"📝 Text analysis tool called: {analysis_type}")

        tool_func = get_tool_function("analyze_text")
        result = tool_func(text, analysis_type)

        if result["success"]:
            analysis_text = f"""Text Analysis Results:
Characters: {result['character_count']} (excluding spaces: {result['character_count_no_spaces']})
Words: {result['word_count']}
Sentences: {result['sentence_count']}
Paragraphs: {result['paragraph_count']}
Average words per sentence: {result['average_words_per_sentence']}"""

            # Add advanced metrics if available
            if 'unique_word_count' in result:
                analysis_text += f"""
Unique words: {result['unique_word_count']}
Vocabulary richness: {result['vocabulary_richness']}
Average word length: {result['average_word_length']}
Most common words: {result['most_common_words'][:3]}"""
        else:
            analysis_text = f"Text Analysis Error: {result['error']}"

        return [TextContent(type="text", text=analysis_text)]

    # TEXT SUMMARIZATION TOOL
    @server.tool("summarize_text")
    async def text_summary_tool(text: str, max_sentences: int = 3) -> List[TextContent]:
        """
        Generate a summary of input text.

        Args:
            text: Text to summarize
            max_sentences: Maximum sentences in summary

        Returns:
            List of TextContent with summary
        """
        logger.info(f"📋 Text summary tool called: max {max_sentences} sentences")

        tool_func = get_tool_function("summarize_text")
        result = tool_func(text, max_sentences)

        if result["success"]:
            summary_text = f"""Text Summary:
Original length: {result['original_length']} characters
Summary length: {result['summary_length']} characters
Reduction: {result['reduction_percentage']}%

Summary:
{result['summary']}"""
        else:
            summary_text = f"Text Summary Error: {result['error']}"

        return [TextContent(type="text", text=summary_text)]

    # DATA GENERATION TOOL
    @server.tool("generate_sample_data")
    async def data_generation_tool(
        data_type: str,
        count: int = 10,
        min_val: int = 1,
        max_val: int = 100,
        decimals: int = 2
    ) -> List[TextContent]:
        """
        Generate sample data for testing purposes.

        Args:
            data_type: Type of data (numbers, floats, names, dates, coordinates)
            count: Number of items to generate
            min_val: Minimum value (for numbers)
            max_val: Maximum value (for numbers)
            decimals: Decimal places (for floats)

        Returns:
            List of TextContent with generated data
        """
        logger.info(f"🎲 Data generation tool called: {count} {data_type} items")

        tool_func = get_tool_function("generate_sample_data")
        kwargs = {"min": min_val, "max": max_val, "decimals": decimals}
        result = tool_func(data_type, count, **kwargs)

        if result["success"]:
            data_text = f"""Generated {result['count']} {result['data_type']} items:
{json.dumps(result['data'][:10], indent=2)}"""
            if len(result['data']) > 10:
                data_text += f"\n... and {len(result['data']) - 10} more items"
        else:
            data_text = f"Data Generation Error: {result['error']}"

        return [TextContent(type="text", text=data_text)]

    # BUSINESS METRICS SIMULATION TOOL
    @server.tool("simulate_business_metrics")
    async def business_simulation_tool(days: int = 30, base_value: float = 1000.0) -> List[TextContent]:
        """
        Simulate business metrics over time.

        Args:
            days: Number of days to simulate
            base_value: Base value for calculations

        Returns:
            List of TextContent with simulation results
        """
        logger.info(f"📈 Business simulation tool called: {days} days")

        tool_func = get_tool_function("simulate_business_metrics")
        result = tool_func(days, base_value)

        if result["success"]:
            summary = result['summary']
            simulation_text = f"""Business Metrics Simulation ({days} days):

Summary:
Total Sales: {summary['total_sales']:,}
Total Customers: {summary['total_customers']:,}
Total Revenue: ${summary['total_revenue']:,.2f}
Average Daily Sales: {summary['average_daily_sales']:,.2f}
Average Daily Revenue: ${summary['average_daily_revenue']:,.2f}
Revenue per Sale: ${summary['average_revenue_per_sale']:.2f}

Sample Daily Data (first 5 days):"""

            for day in result['daily_data'][:5]:
                simulation_text += f"\n{day['date']}: {day['sales']} sales, {day['customers']} customers, ${day['revenue']:.2f} revenue"
        else:
            simulation_text = f"Business Simulation Error: {result['error']}"

        return [TextContent(type="text", text=simulation_text)]

    # TIMESTAMP UTILITY TOOL
    @server.tool("get_timestamp")
    async def timestamp_tool(format_type: str = "iso") -> List[TextContent]:
        """
        Get current timestamp in various formats.

        Args:
            format_type: Format type (iso, unix, readable, all)

        Returns:
            List of TextContent with timestamp information
        """
        logger.info(f"⏰ Timestamp tool called: {format_type} format")

        tool_func = get_tool_function("get_timestamp")
        result = tool_func(format_type)

        if result["success"]:
            timestamp_text = f"Current Timestamp ({format_type} format):\n"
            for key, value in result['timestamps'].items():
                timestamp_text += f"{key}: {value}\n"
            timestamp_text += f"Timezone: {result['timezone']}"
        else:
            timestamp_text = f"Timestamp Error: {result['error']}"

        return [TextContent(type="text", text=timestamp_text)]

    # DATA VALIDATION TOOL
    @server.tool("validate_data")
    async def validation_tool(data: str, format_type: str) -> List[TextContent]:
        """
        Validate data against common formats.

        Args:
            data: Data string to validate
            format_type: Format type (email, phone, url, ip_address, etc.)

        Returns:
            List of TextContent with validation results
        """
        logger.info(f"✅ Validation tool called: {format_type} format")

        tool_func = get_tool_function("validate_data")
        result = tool_func(data, format_type)

        if result["success"]:
            validation_text = f"""Data Validation Results:
Data: {result['data']}
Format: {result['format_type']}
Valid: {'✅ Yes' if result['is_valid'] else '❌ No'}"""
        else:
            validation_text = f"Validation Error: {result['error']}"

        return [TextContent(type="text", text=validation_text)]

    # CUSTOM BUSINESS TOOLS

    @server.tool("analyze_sales_data")
    async def sales_analysis_tool(period: str = "monthly", region: str = "all") -> List[TextContent]:
        """
        Analyze sales data for business insights.

        Args:
            period: Analysis period (daily, weekly, monthly, yearly)
            region: Geographic region (all, north, south, east, west)

        Returns:
            List of TextContent with sales analysis
        """
        logger.info(f"📊 Sales analysis tool called: {period}, {region}")

        tool_func = get_tool_function("analyze_sales_data")
        result = tool_func(period, region)

        if result["success"]:
            analysis_text = f"""Sales Analysis Report:
                            Period: {result['period']}
                            Region: {result['region']}
                            Total Sales: ${result['total_sales']:,.2f}
                            Growth Rate: {result['growth_rate']}%

                            Top Products: {', '.join(result['top_products'])}

                            Recommendations:"""
            for rec in result['recommendations']:
                analysis_text += f"\n• {rec}"
        else:
            analysis_text = f"Sales Analysis Error: {result['error']}"

        return [TextContent(type="text", text=analysis_text)]

    @server.tool("generate_report")
    async def report_generation_tool(report_type: str = "summary", format: str = "json") -> List[TextContent]:
        """
        Generate business reports.

        Args:
            report_type: Type of report (summary, detailed, executive)
            format: Output format (json, text, csv)

        Returns:
            List of TextContent with generated report
        """
        logger.info(f"📋 Report generation tool called: {report_type} report")

        tool_func = get_tool_function("generate_report")
        result = tool_func(report_type, format)

        if result["success"]:
            summary = result['summary']
            report_text = f"""Business Report ({result['report_type']}):
Generated: {result['generated_at']}

Key Performance Metrics:
• Total Revenue: ${summary['total_revenue']:,.2f}
• Total Orders: {summary['total_orders']:,}
• Customer Satisfaction: {summary['customer_satisfaction']}/5.0
• Growth Rate: {summary['growth_rate']}%

Key Metrics Trends:"""

            for metric in result['key_metrics']:
                trend_icon = "📈" if metric['trend'] == "up" else "📊" if metric['trend'] == "stable" else "📉"
                report_text += f"\n• {metric['metric']}: {metric['value']} {trend_icon}"

            if 'executive_summary' in result:
                report_text += f"\n\nExecutive Summary:\n{result['executive_summary']}"
        else:
            report_text = f"Report Generation Error: {result['error']}"

        return [TextContent(type="text", text=report_text)]

    logger.info(f"✅ Registered {len(AVAILABLE_TOOLS)} tools with MCP server")

# ==============================================================================
# SERVER INITIALIZATION AND STARTUP
# ==============================================================================

async def main(transport: str = "stdio", host: str = "localhost", port: int = 8080):
    """
    Main function to start the MCP server.

    This initializes the server, registers all tools, and starts listening
    for MCP protocol messages via the specified transport.

    Args:
        transport: Transport type ("stdio" or "sse")
        host: Host address for SSE server (default: localhost) - Note: May not be configurable in all FastMCP versions
        port: Port for SSE server (default: 8080) - Note: May not be configurable in all FastMCP versions
    """

    logger.info("🚀 Starting Local MCP Server...")
    logger.info("📡 Server Name: local-custom-tools-server")
    logger.info(f"🔧 Transport: {transport}")

    if transport == "sse":
        logger.info(f"🌐 SSE Server will start (host/port may be determined by FastMCP defaults)")
        logger.info(f"🔧 Requested: http://{host}:{port} (may not be configurable)")
    else:
        logger.info("📡 Transport: stdio (stdin/stdout)")

    # Register all our custom tools
    register_all_tools()

    logger.info("✅ MCP Server ready - waiting for client connections...")

    # Start the server based on transport type
    try:
        if transport == "sse":
            # Start SSE server - FastMCP handles host/port internally
            # Different FastMCP versions may have different SSE configuration methods
            logger.info("🌐 Starting SSE server with FastMCP defaults...")
            await server.run_sse_async()
        else:
            # Start stdio server (default)
            await server.run_stdio_async()
    except KeyboardInterrupt:
        logger.info("🔚 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Local MCP Server with multiple transport options")
    parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport type: stdio (default) or sse"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host address for SSE server (default: localhost)"
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8080,
        help="Port for SSE server (default: 8080)"
    )
    return parser.parse_args()

# Server startup
if __name__ == "__main__":
    """
    Entry point for the MCP server.

    When this script is executed, it starts the MCP server process that
    will communicate with clients via the Model Context Protocol.

    The server supports two transport modes:
    1. stdio: Communication via stdin/stdout (default)
    2. sse: HTTP Server-Sent Events for remote access

    Usage examples:
        # Default stdio mode
        python local_server.py

        # SSE mode with default settings (localhost:8080)
        python local_server.py --transport sse

        # SSE mode with custom host and port
        python local_server.py --transport sse --host 0.0.0.0 --port 9000

    The server runs indefinitely until:
    1. The client disconnects (stdio mode)
    2. The process is terminated (Ctrl+C)
    3. An unhandled error occurs
    """

    # Parse command line arguments
    args = parse_args()

    # Ensure proper event loop handling
    try:
        asyncio.run(main(transport=args.transport, host=args.host, port=args.port))
    except KeyboardInterrupt:
        print(f"\n👋 Local MCP Server ({args.transport} mode) shutdown complete")
    except Exception as e:
        print(f"❌ Fatal server error: {e}")
        sys.exit(1)
