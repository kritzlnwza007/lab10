import json
import math
from litellm import completion
from config import MODEL


calculator_tools = [
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


TOOL_IMPL = {
    "add": lambda a, b: float(a)+float(b),
    "area_circle": lambda radius: math.pi*float(radius)**2,
}


messages = [{"role": "user",
             "content": "What is (25 + 17), then use the result as radius to compute circle area."}]

print("first LLM request :", messages)
# Let the model propose a tool
first = completion(model=MODEL, messages=messages,
                   functions=calculator_tools, function_call="auto")
msg = first.choices[0].message
fc = getattr(msg, "function_call", None) if hasattr(
    msg, "function_call") else msg.get("function_call")
print("=== INTERMEDIATE (1) ===")
print("name:", getattr(fc, "name", None) if fc else None)
raw_args = getattr(fc, "arguments", None) if fc else None
print("arguments (raw):", raw_args)


if fc:
    name = fc.name
    args = json.loads(raw_args or "{}")
    result = TOOL_IMPL[name](**args)
    # return tool result
    messages.append({"role": "assistant", "content": None,
                    "function_call": {"name": name, "arguments": raw_args}})
    messages.append({"role": "function", "name": name,
                    "content": json.dumps({"result": result})})

    print("second LLM request:", messages)
    second = completion(model=MODEL, messages=messages,
                        functions=calculator_tools, function_call="auto")
    msg2 = second.choices[0].message
    fc2 = getattr(msg2, "function_call", None) if hasattr(
        msg2, "function_call") else msg2.get("function_call")
    print("=== INTERMEDIATE (2) ===")
    print("name:", getattr(fc2, "name", None) if fc2 else None)
    print("arguments:", getattr(fc2, "arguments", None) if fc2 else None)
    
    


    if fc2:
        name2 = fc2.name
        args2 = json.loads(fc2.arguments)
        result2 = TOOL_IMPL[name2](**args2)
        messages.append({"role": "assistant", "content": None, "function_call": {
                        "name": name2, "arguments": fc2.arguments}})
        messages.append({"role": "function", "name": name2,
                        "content": json.dumps({"result": result2})})
        print("Final LLM request: ", messages)
        final = completion(model=MODEL, messages=messages)
        print("FINAL:", final.choices[0].message["content"])
    else:
        print("FINAL:", getattr(msg2, "content", None) or msg2["content"])
else:print("No tool proposal; assistant said:", getattr(msg, "content", None) or msg["content"])

