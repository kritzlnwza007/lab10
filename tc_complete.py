# tc_complete.py - provided implementation
# Source adapted from the uploaded file
# Imports and dependencies
from litellm import completion
import json
import math
from typing import List, Dict, Any
from config import MODEL

# Tool implementations - Calculator functions with schema definitions
class CalculatorTools:
    def add(self, a: float, b: float) -> float:
        return float(a) + float(b)
    
    def area_circle(self, radius: float) -> float:
        return math.pi * float(radius) ** 2
    
    @classmethod
    def get_schemas(cls):
        """Return the function schemas for all tools in this class"""
        return [
            {
                "name": "add",
                "description": "Add two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            },
            {
                "name": "area_circle",
                "description": "Area of a circle",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "radius": {"type": "number"}
                    },
                    "required": ["radius"]
                }
            }
        ]
    
    def register_all_tools(self, executor):
        """Register all tools in this class with the executor"""
        schemas = self.get_schemas()
        executor.register_tool("add", self.add, schemas[0])
        executor.register_tool("area_circle", self.area_circle, schemas[1])

class ToolExecutor:
    """Main executor class that manages tools and handles LLM function calling"""
    def __init__(self):
        self.tools = {}
        self.tool_schemas = []
    
    def register_tool(self, name: str, func: callable, schema: dict):
        """Register a single tool with its execution function and schema"""
        self.tools[name] = func
        self.tool_schemas.append(schema)
    
    def register_tools(self, tool_class_instance):
        """Register all tools from a tool class instance"""
        schemas = tool_class_instance.get_schemas()
        for i, schema in enumerate(schemas):
            tool_name = schema["name"]
            tool_func = getattr(tool_class_instance, tool_name)
            self.register_tool(tool_name, tool_func, schema)
    
    def execute_with_tools(self, user_message: str, model: str = MODEL) -> str:
        """Execute user request with available tools - main conversation loop"""
        messages = [{"role": "user", "content": user_message}]
        
        while True:
            # Step 1: Get LLM response with tool options
            response = completion(
                model=model,
                messages=messages,
                functions=self.tool_schemas,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            # Step 2: Check if LLM wants to call a function
            if not getattr(message, "function_call", None):
                return getattr(message, "content", None) or message.get("content")
            
            # Step 3: Execute the requested tool
            tool_name = message.function_call.name
            tool_args = json.loads(message.function_call.arguments)
            
            if tool_name in self.tools:
                try:
                    tool_result = self.tools[tool_name](**tool_args)
                    
                    # Step 4: Add tool call and result to conversation history
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": tool_name,
                            "arguments": message.function_call.arguments
                        }
                    })
                    messages.append({
                        "role": "function",
                        "name": tool_name,
                        "content": str(tool_result)
                    })
                    
                except Exception as e:
                    # Handle tool execution errors
                    messages.append({
                        "role": "function", 
                        "name": tool_name,
                        "content": f"Error: {e}"
                    })
            else:
                return f"Tool {tool_name} not available"

# Demo usage and testing
if __name__ == "__main__":
    executor = ToolExecutor()

    # Register calculator tools using the new register_tools method
    calc = CalculatorTools()
    executor.register_tools(calc)

    # Execute user requests and display results
    result1 = executor.execute_with_tools("What's 15 plus 27?")
    result2 = executor.execute_with_tools("Calculate the area of a circle with radius 5")

    print(result1)  # The result is 42
    print(result2)  # The area is approximately 78.54 square units
