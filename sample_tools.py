"""
Sample Tools for MCP Server
============================

This module contains sample tool implementations that will be registered
with the local MCP server. These tools demonstrate various capabilities
and provide a foundation for adding custom business logic.

Each tool is a simple Python function that:
1. Takes defined parameters as input
2. Performs some operation (calculation, data processing, API call, etc.)
3. Returns a result in a consistent format

Key Design Principles:
- Simple, focused functions that do one thing well
- Clear parameter validation and error handling
- Consistent return formats for easy integration
- Well-documented for easy extension and modification

Author: Assistant
Date: August 15, 2025
"""

import json
import math
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Set up logging for tool operations
logger = logging.getLogger(__name__)

# ==============================================================================
# MATHEMATICAL CALCULATION TOOLS
# ==============================================================================

def calculate_math(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate mathematical expressions.
    
    This tool provides secure mathematical computation without the security
    risks of unrestricted eval(). Supports basic arithmetic, trigonometry,
    and common mathematical functions.
    
    Args:
        expression: Mathematical expression as string (e.g., "2 + 2", "sqrt(16)")
        
    Returns:
        Dict with calculation result or error information
        
    Example:
        calculate_math("15 * 23 + sqrt(144)") -> {"result": 357, "success": True}
    """
    
    logger.info(f"🧮 Math calculation requested: {expression}")
    
    try:
        # Define safe mathematical functions and constants
        safe_math_namespace = {
            # Basic functions
            "abs": abs, "round": round, "min": min, "max": max, "sum": sum, "pow": pow,
            
            # Math functions
            "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "log": math.log, "log10": math.log10, "exp": math.exp,
            "floor": math.floor, "ceil": math.ceil,
            
            # Constants
            "pi": math.pi, "e": math.e,
            
            # Prevent dangerous operations
            "__builtins__": {}
        }
        
        # Clean and prepare expression
        clean_expression = expression.replace("^", "**")  # Convert ^ to **
        clean_expression = clean_expression.strip()
        
        # Evaluate safely
        result = eval(clean_expression, safe_math_namespace)
        
        logger.info(f"✅ Calculation successful: {expression} = {result}")
        
        return {
            "expression": expression,
            "result": result,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "mathematical_calculation"
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Calculation failed: {expression} - {error_msg}")
        
        return {
            "expression": expression,
            "error": error_msg,
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "mathematical_calculation"
        }

def generate_statistics(data: List[float]) -> Dict[str, Any]:
    """
    Calculate statistical measures for a dataset.
    
    Args:
        data: List of numerical values
        
    Returns:
        Dict with statistical analysis results
    """
    
    logger.info(f"📊 Statistical analysis requested for {len(data)} data points")
    
    try:
        if not data:
            raise ValueError("Dataset cannot be empty")
        
        # Calculate basic statistics
        n = len(data)
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / n
        std_dev = math.sqrt(variance)
        
        sorted_data = sorted(data)
        median = sorted_data[n // 2] if n % 2 == 1 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
        
        stats = {
            "count": n,
            "mean": round(mean, 4),
            "median": round(median, 4),
            "std_deviation": round(std_dev, 4),
            "variance": round(variance, 4),
            "min": min(data),
            "max": max(data),
            "range": max(data) - min(data),
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "statistical_analysis"
        }
        
        logger.info(f"✅ Statistics calculated successfully")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Statistical analysis failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "statistical_analysis"
        }

# ==============================================================================
# TEXT PROCESSING TOOLS
# ==============================================================================

def analyze_text(text: str, analysis_type: str = "all") -> Dict[str, Any]:
    """
    Perform various text analysis operations.
    
    Args:
        text: Input text to analyze
        analysis_type: Type of analysis ("basic", "advanced", "all")
        
    Returns:
        Dict with text analysis results
    """
    
    logger.info(f"📝 Text analysis requested: {analysis_type} for {len(text)} characters")
    
    try:
        # Basic analysis
        word_count = len(text.split())
        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", ""))
        sentence_count = len([s for s in text.split('.') if s.strip()])
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        result = {
            "character_count": char_count,
            "character_count_no_spaces": char_count_no_spaces,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "average_words_per_sentence": round(word_count / max(sentence_count, 1), 2),
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "text_analysis"
        }
        
        # Advanced analysis if requested
        if analysis_type in ["advanced", "all"]:
            words = text.lower().split()
            unique_words = set(words)
            
            # Most common words (simple frequency count)
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            most_common = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            
            result.update({
                "unique_word_count": len(unique_words),
                "vocabulary_richness": round(len(unique_words) / max(len(words), 1), 3),
                "most_common_words": most_common,
                "average_word_length": round(sum(len(word) for word in words) / max(len(words), 1), 2)
            })
        
        logger.info(f"✅ Text analysis completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Text analysis failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "text_analysis"
        }

def generate_text_summary(text: str, max_sentences: int = 3) -> Dict[str, Any]:
    """
    Generate a simple extractive summary of text.
    
    Args:
        text: Input text to summarize
        max_sentences: Maximum number of sentences in summary
        
    Returns:
        Dict with summary and metadata
    """
    
    logger.info(f"📋 Text summary requested: max {max_sentences} sentences")
    
    try:
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) <= max_sentences:
            summary = text
            reduction = 0
        else:
            # Simple extractive summarization - take first, middle, and last sentences
            if max_sentences == 1:
                selected = [sentences[0]]
            elif max_sentences == 2:
                selected = [sentences[0], sentences[-1]]
            else:
                middle_idx = len(sentences) // 2
                selected = [sentences[0], sentences[middle_idx], sentences[-1]]
                
                # Add more sentences if requested and available
                remaining_slots = max_sentences - 3
                if remaining_slots > 0 and len(sentences) > 3:
                    step = len(sentences) // (remaining_slots + 1)
                    for i in range(1, remaining_slots + 1):
                        idx = i * step
                        if idx < len(sentences) and sentences[idx] not in selected:
                            selected.append(sentences[idx])
            
            summary = '. '.join(selected[:max_sentences]) + '.'
            reduction = round((1 - len(summary) / len(text)) * 100, 1)
        
        result = {
            "original_length": len(text),
            "summary_length": len(summary),
            "reduction_percentage": reduction,
            "original_sentences": len(sentences),
            "summary_sentences": min(len(sentences), max_sentences),
            "summary": summary,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "text_summary"
        }
        
        logger.info(f"✅ Summary generated: {reduction}% reduction")
        return result
        
    except Exception as e:
        logger.error(f"❌ Text summarization failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "text_summary"
        }

# ==============================================================================
# DATA GENERATION AND SIMULATION TOOLS
# ==============================================================================

def generate_sample_data(data_type: str, count: int = 10, **kwargs) -> Dict[str, Any]:
    """
    Generate sample data for testing and demonstration purposes.
    
    Args:
        data_type: Type of data to generate ("numbers", "names", "dates", "coordinates")
        count: Number of data points to generate
        **kwargs: Additional parameters specific to data type
        
    Returns:
        Dict with generated data and metadata
    """
    
    logger.info(f"🎲 Sample data generation: {count} {data_type} items")
    
    try:
        if data_type == "numbers":
            min_val = kwargs.get("min", 1)
            max_val = kwargs.get("max", 100)
            data = [random.randint(min_val, max_val) for _ in range(count)]
            
        elif data_type == "floats":
            min_val = kwargs.get("min", 0.0)
            max_val = kwargs.get("max", 1.0)
            decimals = kwargs.get("decimals", 2)
            data = [round(random.uniform(min_val, max_val), decimals) for _ in range(count)]
            
        elif data_type == "names":
            first_names = ["Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry", "Ivy", "Jack"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
            data = [f"{random.choice(first_names)} {random.choice(last_names)}" for _ in range(count)]
            
        elif data_type == "dates":
            start_date = datetime.now() - timedelta(days=365)
            data = []
            for _ in range(count):
                random_days = random.randint(0, 365)
                date = start_date + timedelta(days=random_days)
                data.append(date.strftime("%Y-%m-%d"))
                
        elif data_type == "coordinates":
            # Generate random lat/lng coordinates
            data = []
            for _ in range(count):
                lat = round(random.uniform(-90, 90), 6)
                lng = round(random.uniform(-180, 180), 6)
                data.append({"latitude": lat, "longitude": lng})
                
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        result = {
            "data_type": data_type,
            "count": len(data),
            "parameters": kwargs,
            "data": data,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "data_generation"
        }
        
        logger.info(f"✅ Generated {len(data)} {data_type} items")
        return result
        
    except Exception as e:
        logger.error(f"❌ Data generation failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "data_generation"
        }

def simulate_business_metrics(days: int = 30, base_value: float = 1000.0) -> Dict[str, Any]:
    """
    Simulate business metrics over time for testing and demonstration.
    
    Args:
        days: Number of days to simulate
        base_value: Base value for metrics
        
    Returns:
        Dict with simulated business data
    """
    
    logger.info(f"📈 Business metrics simulation: {days} days from base {base_value}")
    
    try:
        dates = []
        sales = []
        customers = []
        revenue = []
        
        current_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            # Add some realistic variation and trends
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Sales with weekly pattern and random variation
            weekly_factor = 1.2 if current_date.weekday() < 5 else 0.8  # Higher weekdays
            daily_sales = int(base_value * weekly_factor * random.uniform(0.8, 1.2))
            
            # Customer count correlated with sales
            daily_customers = int(daily_sales * random.uniform(0.1, 0.3))
            
            # Revenue with some profit margin variation
            daily_revenue = daily_sales * random.uniform(1.1, 1.4)
            
            dates.append(date_str)
            sales.append(daily_sales)
            customers.append(daily_customers)
            revenue.append(round(daily_revenue, 2))
            
            current_date += timedelta(days=1)
        
        # Calculate summary statistics
        total_sales = sum(sales)
        total_customers = sum(customers)
        total_revenue = sum(revenue)
        avg_daily_sales = round(total_sales / days, 2)
        avg_daily_revenue = round(total_revenue / days, 2)
        
        result = {
            "simulation_period": f"{days} days",
            "base_value": base_value,
            "summary": {
                "total_sales": total_sales,
                "total_customers": total_customers,
                "total_revenue": round(total_revenue, 2),
                "average_daily_sales": avg_daily_sales,
                "average_daily_revenue": avg_daily_revenue,
                "average_revenue_per_sale": round(total_revenue / total_sales, 2)
            },
            "daily_data": [
                {
                    "date": dates[i],
                    "sales": sales[i],
                    "customers": customers[i],
                    "revenue": revenue[i]
                }
                for i in range(days)
            ],
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "business_simulation"
        }
        
        logger.info(f"✅ Business simulation completed: {total_sales} total sales")
        return result
        
    except Exception as e:
        logger.error(f"❌ Business simulation failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "business_simulation"
        }

# ==============================================================================
# UTILITY AND SYSTEM TOOLS
# ==============================================================================

def get_system_timestamp(format_type: str = "iso") -> Dict[str, Any]:
    """
    Get current system timestamp in various formats.
    
    Args:
        format_type: Format type ("iso", "unix", "readable", "all")
        
    Returns:
        Dict with timestamp information
    """
    
    logger.info(f"⏰ Timestamp requested: {format_type} format")
    
    try:
        now = datetime.now()
        
        timestamps = {
            "iso": now.isoformat(),
            "unix": int(now.timestamp()),
            "readable": now.strftime("%Y-%m-%d %H:%M:%S"),
            "utc_iso": datetime.utcnow().isoformat() + "Z",
            "date_only": now.strftime("%Y-%m-%d"),
            "time_only": now.strftime("%H:%M:%S")
        }
        
        if format_type == "all":
            result_data = timestamps
        else:
            result_data = {format_type: timestamps.get(format_type, timestamps["iso"])}
        
        result = {
            "requested_format": format_type,
            "timestamps": result_data,
            "timezone": str(now.astimezone().tzinfo),
            "success": True,
            "type": "system_timestamp"
        }
        
        logger.info(f"✅ Timestamp generated: {format_type}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Timestamp generation failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "type": "system_timestamp"
        }

def validate_data_format(data: str, format_type: str) -> Dict[str, Any]:
    """
    Validate data against common formats (email, phone, URL, etc.).
    
    Args:
        data: Data string to validate
        format_type: Type of format to validate against
        
    Returns:
        Dict with validation results
    """
    
    logger.info(f"✅ Data validation requested: {format_type} for '{data[:20]}...'")
    
    try:
        import re
        
        validation_patterns = {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "phone": r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$',
            "url": r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
            "ip_address": r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            "credit_card": r'^[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}[-\s]?[0-9]{4}$',
            "ssn": r'^\d{3}-?\d{2}-?\d{4}$'
        }
        
        if format_type not in validation_patterns:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        pattern = validation_patterns[format_type]
        is_valid = bool(re.match(pattern, data.strip()))
        
        result = {
            "data": data,
            "format_type": format_type,
            "is_valid": is_valid,
            "pattern_used": pattern,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "data_validation"
        }
        
        logger.info(f"✅ Validation completed: {is_valid}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Data validation failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "data_validation"
        }

# ==============================================================================
# CUSTOM BUSINESS TOOLS SECTION
# ==============================================================================
# 
# ADD YOUR CUSTOM TOOLS HERE!
# 
# Follow the pattern established above:
# 1. Clear function name and docstring
# 2. Type hints for parameters and return value
# 3. Logging for operations
# 4. Consistent error handling
# 5. Standardized return format with success/error status
# 
# Example template:
#
# def your_custom_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
#     """
#     Description of what your tool does.
#     
#     Args:
#         param1: Description of parameter 1
#         param2: Description of parameter 2 with default value
#         
#     Returns:
#         Dict with tool results
#     """
#     
#     logger.info(f"🔧 Your custom tool called with {param1}, {param2}")
#     
#     try:
#         # Your tool logic here
#         result = perform_custom_operation(param1, param2)
#         
#         return {
#             "result": result,
#             "success": True,
#             "timestamp": datetime.now().isoformat(),
#             "type": "custom_tool"
#         }
#         
#     except Exception as e:
#         logger.error(f"❌ Custom tool failed: {e}")
#         return {
#             "error": str(e),
#             "success": False,
#             "timestamp": datetime.now().isoformat(),
#             "type": "custom_tool"
#         }

def analyze_sales_data(period: str = "monthly", region: str = "all") -> Dict[str, Any]:
    """
    Example custom business tool - analyze sales data.
    
    This is a placeholder that demonstrates how you would structure
    a custom business tool. Replace with your actual business logic.
    
    Args:
        period: Analysis period ("daily", "weekly", "monthly", "yearly")
        region: Geographic region filter ("all", "north", "south", "east", "west")
        
    Returns:
        Dict with sales analysis results
    """
    
    logger.info(f"📊 Sales analysis requested: {period} period, {region} region")
    
    try:
        # Simulate sales analysis - replace with real business logic
        base_sales = 50000 if period == "monthly" else 12000
        region_multiplier = {"all": 1.0, "north": 1.2, "south": 0.9, "east": 1.1, "west": 0.8}.get(region, 1.0)
        
        simulated_sales = base_sales * region_multiplier * random.uniform(0.8, 1.2)
        
        analysis = {
            "period": period,
            "region": region,
            "total_sales": round(simulated_sales, 2),
            "growth_rate": round(random.uniform(-5, 15), 2),  # % growth
            "top_products": ["Product A", "Product B", "Product C"],
            "recommendations": [
                "Focus marketing on high-growth segments",
                "Optimize inventory for seasonal trends",
                "Expand successful product lines"
            ],
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "type": "sales_analysis"
        }
        
        logger.info(f"✅ Sales analysis completed: ${simulated_sales:,.2f} total sales")
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Sales analysis failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "sales_analysis"
        }

def generate_report(report_type: str = "summary", format: str = "json") -> Dict[str, Any]:
    """
    Example custom business tool - generate various types of reports.
    
    Args:
        report_type: Type of report ("summary", "detailed", "executive")
        format: Output format ("json", "text", "csv")
        
    Returns:
        Dict with generated report
    """
    
    logger.info(f"📋 Report generation: {report_type} report in {format} format")
    
    try:
        # Simulate report generation - replace with real logic
        report_data = {
            "report_type": report_type,
            "format": format,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_revenue": 125000.50,
                "total_orders": 342,
                "customer_satisfaction": 4.2,
                "growth_rate": 8.5
            },
            "key_metrics": [
                {"metric": "Conversion Rate", "value": "3.2%", "trend": "up"},
                {"metric": "Average Order Value", "value": "$365.50", "trend": "stable"},
                {"metric": "Customer Retention", "value": "78%", "trend": "up"}
            ],
            "success": True,
            "type": "business_report"
        }
        
        if report_type == "detailed":
            report_data["detailed_sections"] = [
                "Financial Performance",
                "Customer Analytics", 
                "Product Performance",
                "Market Analysis"
            ]
        elif report_type == "executive":
            report_data["executive_summary"] = "Strong quarterly performance with revenue growth exceeding targets."
        
        logger.info(f"✅ {report_type} report generated successfully")
        return report_data
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        return {
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "type": "business_report"
        }

# ==============================================================================
# TOOL REGISTRY
# ==============================================================================

# This dictionary maps tool names to their implementations
# The MCP server will use this to register and route tool calls
AVAILABLE_TOOLS = {
    # Mathematical tools
    "calculate": calculate_math,
    "generate_statistics": generate_statistics,
    
    # Text processing tools
    "analyze_text": analyze_text,
    "summarize_text": generate_text_summary,
    
    # Data generation tools
    "generate_sample_data": generate_sample_data,
    "simulate_business_metrics": simulate_business_metrics,
    
    # Utility tools
    "get_timestamp": get_system_timestamp,
    "validate_data": validate_data_format,
    
    # Custom business tools (examples)
    "analyze_sales_data": analyze_sales_data,
    "generate_report": generate_report,
    
    # ADD YOUR CUSTOM TOOLS HERE:
    # "your_tool_name": your_tool_function,
}

def get_tool_function(tool_name: str):
    """
    Get a tool function by name.
    
    Args:
        tool_name: Name of the tool to retrieve
        
    Returns:
        Tool function or None if not found
    """
    return AVAILABLE_TOOLS.get(tool_name)

def list_available_tools() -> List[str]:
    """
    Get list of all available tool names.
    
    Returns:
        List of tool names
    """
    return list(AVAILABLE_TOOLS.keys())

# Test function for development
if __name__ == "__main__":
    # Quick test of tools during development
    print("🧪 Testing sample tools...")
    
    # Test math calculation
    result = calculate_math("15 * 23 + sqrt(144)")
    print(f"Math test: {result}")
    
    # Test text analysis
    result = analyze_text("This is a sample text for testing. It has multiple sentences.")
    print(f"Text analysis test: {result}")
    
    # Test data generation
    result = generate_sample_data("numbers", 5, min=1, max=10)
    print(f"Data generation test: {result}")
    
    print("✅ All tests completed!")
