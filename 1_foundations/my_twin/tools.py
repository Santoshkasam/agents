import requests
import os
import json

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(message):
    print(f"Push: {message}")
    if not pushover_user or not pushover_token:
        raise RuntimeError("Pushover is not configured; set PUSHOVER_USER and PUSHOVER_TOKEN.")

    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    response = requests.post(pushover_url, data=payload, timeout=10)
    response.raise_for_status()

# Define a function to record user details
def record_user_details(email, name = "Name not provided", notes = "No notes provided"):
    push(f"The visitor {name} with email-id {email}. Notes: {notes}")
    return "OK"

# Define a funciton to record unknown questions
def record_unknown_question(question):
    with open("unknown_question.txt", "a", encoding="utf-8") as f:
        f.write(question + "\n")
    return "OK"

# Json description of the record_user_details function that will be passed onto the llm as tool description
record_user_details_json = {
    "name": "record_user_details",
    "description": "use this tool to record the details of the user ",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type":"string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The name of this user"},
            "notes": {"type": "string", "description": "Any useful additional information from the conversation, that serves as a context for future conversation"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

# Json description of the record_unknown_question function that will be passed onto the llm as tool description
record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "always use this tool to record a user's question that you couldn't answer with the information given to you",
    "parameters": {
        "type": "object",
        "properties":{
            "question": {"type": "string", "description": "The question that you couldn't answer"},   
        },
        "required": ["question"],
        "additionalProperties": False
    },
}

# define the tools list. This will be fed to the llm
tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question
}

# The function that execute each tool_call in tool_calls returned by the llm, and returns the results of all tool_calls 
def handle_tool_calls(tool_calls):
    results=[]
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments)
        
        print(f"Result of tool call to {tool_name} is: {json.dumps(result)}", flush = True)
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    
    return results