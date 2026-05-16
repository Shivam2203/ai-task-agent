"""
Tool executor for agent actions.

Provides tools for search and Python code execution that the agent can use.
"""
import sys
import io
import traceback
from typing import Any, Dict, List, Optional
from contextlib import redirect_stdout, redirect_stderr

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ToolExecutor:
    """
    Executor for agent tools including search and code execution.
    
    Provides a safe interface for executing various tools that the agent
    can use during task completion.
    """
    
    def __init__(self):
        """Initialize tool executor."""
        self.available_tools = {
            "search": self.search_tool,
            "python_exec": self.python_exec_tool,
            "web_search": self.web_search_tool,
        }
        logger.info(f"Initialized ToolExecutor with {len(self.available_tools)} tools")
    
    async def execute(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result
            
        Example:
            ```python
            executor = ToolExecutor()
            result = await executor.execute(
                "python_exec",
                {"code": "print('Hello, World!')"}
            )
            ```
        """
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.available_tools.keys())
            }
        
        try:
            tool_func = self.available_tools[tool_name]
            result = await tool_func(tool_input)
            logger.info(f"Tool '{tool_name}' executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    async def search_tool(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple search tool (placeholder for RAG integration).
        
        Args:
            tool_input: Dict with 'query' key
            
        Returns:
            Search results
        """
        query = tool_input.get("query", "")
        
        if not query:
            return {
                "success": False,
                "error": "No query provided"
            }
        
        # TODO: Integrate with RAG system for actual search
        # For now, return a placeholder
        logger.info(f"Search query: {query}")
        
        return {
            "success": True,
            "query": query,
            "results": [
                {
                    "title": "Search Result 1",
                    "content": f"This is a placeholder result for: {query}",
                    "relevance": 0.95
                }
            ],
            "message": "Search functionality will be integrated with RAG system"
        }
    
    async def python_exec_tool(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Python code in a controlled environment.
        
        Args:
            tool_input: Dict with 'code' key containing Python code
            
        Returns:
            Execution result with stdout, stderr, and return value
            
        Warning:
            This executes arbitrary code. In production, use a sandboxed
            environment or container for security.
        """
        code = tool_input.get("code", "")
        
        if not code:
            return {
                "success": False,
                "error": "No code provided"
            }
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Create a restricted namespace
            namespace = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    "bool": bool,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                }
            }
            
            # Execute code with output capture
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, namespace)
            
            stdout_value = stdout_capture.getvalue()
            stderr_value = stderr_capture.getvalue()
            
            logger.info(f"Python code executed successfully (output: {len(stdout_value)} chars)")
            
            return {
                "success": True,
                "stdout": stdout_value,
                "stderr": stderr_value,
                "namespace": {k: str(v) for k, v in namespace.items() if not k.startswith("__")}
            }
            
        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error(f"Python execution error: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "traceback": error_msg,
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue()
            }
    
    async def web_search_tool(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Web search tool (placeholder for external API integration).
        
        Args:
            tool_input: Dict with 'query' key
            
        Returns:
            Web search results
        """
        query = tool_input.get("query", "")
        
        if not query:
            return {
                "success": False,
                "error": "No query provided"
            }
        
        # TODO: Integrate with web search API (e.g., Serper, Brave Search)
        logger.info(f"Web search query: {query}")
        
        return {
            "success": True,
            "query": query,
            "results": [
                {
                    "title": "Web Result 1",
                    "url": "https://example.com/result1",
                    "snippet": f"Web search result for: {query}",
                }
            ],
            "message": "Web search API integration pending"
        }
    
    def get_tool_descriptions(self) -> List[Dict[str, str]]:
        """
        Get descriptions of available tools for the agent.
        
        Returns:
            List of tool descriptions
        """
        return [
            {
                "name": "search",
                "description": "Search the knowledge base for relevant information",
                "parameters": {
                    "query": "The search query string"
                }
            },
            {
                "name": "python_exec",
                "description": "Execute Python code and return the output",
                "parameters": {
                    "code": "Python code to execute"
                }
            },
            {
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": {
                    "query": "The web search query"
                }
            }
        ]


# Global tool executor instance
tool_executor = ToolExecutor()

# Made with Bob
