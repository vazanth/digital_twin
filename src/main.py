from dotenv import load_dotenv

import gradio as gr

from google import genai
from google.genai import types
from context import prompt
from tools import record_email, record_phone

load_dotenv()

client = genai.Client()

chat = client.chats.create(
    model="gemini-2.5-flash",
    config= types.GenerateContentConfig(
        system_instruction=prompt,
        tools=[
            record_email,
            record_phone
        ]
    )
)

def send_message(message, _):
    response = chat.send_message(message)
    return response.text


if __name__ == "__main__":
    gr.ChatInterface(
    fn=send_message,
    title="Digital Twin",
    description="A digital twin of me, powered by Gemini 2.5"
).launch(inbrowser=True)