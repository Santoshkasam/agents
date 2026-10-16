from dotenv import load_dotenv

# Load configuration before importing modules that read environment variables.
load_dotenv(override=True)

from openai import OpenAI
import gradio as gr
from context import twin_system_prompt
import json
from tools import tools, handle_tool_calls
from styles import CSS, JS, EXAMPLES


# start an openai client
openai = OpenAI() 

def chat(message, history):
    messages = [{"role": "system", "content": twin_system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages, tools = tools)

    # Loop to perform tool calls
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages, tools = tools)

    return response.choices[0].message.content

if __name__ == "__main__":
    gr.ChatInterface(chat,
                     examples=EXAMPLES,
                     title="Digital Twin",
                     description="Talk to my AI Twin about my career",
                     chatbot = gr.Chatbot(show_label = False)
    ).launch(css=CSS, js=JS, theme=gr.themes.Base(), inbrowser=True)