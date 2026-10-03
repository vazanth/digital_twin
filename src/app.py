from dotenv import load_dotenv
import json
import tools
from pathlib import Path

import gradio as gr

from google import genai

from context import prompt, EXAMPLES


load_dotenv()

AVAILABLE_TOOLS = {
    "record_email": tools.record_email,
    "record_phone_number": tools.record_phone_number,
    "record_inquiry": tools.record_inquiry,
}

client = genai.Client()

record_email_tool = json.loads(Path("src/tool_schemas/record_email.json").read_text())
record_phone_tool = json.loads(
    Path("src/tool_schemas/record_phone_number.json").read_text()
)
record_inquiry_tool = json.loads(
    Path("src/tool_schemas/record_inquiry.json").read_text()
)


def create_interaction(input, previous_interaction_id=None):
    print("  calling with previous_interaction_id:", previous_interaction_id)
    return client.interactions.create(
        model="gemini-2.5-flash",
        input=input,
        system_instruction=prompt,
        tools=[
            {"type": "function", **record_inquiry_tool},
            {"type": "function", **record_email_tool},
            {"type": "function", **record_phone_tool},
        ],
        previous_interaction_id=previous_interaction_id,
        generation_config={
            "thinking_level": "low",
            "thinking_summaries": "auto",
        },
        stream=True,
    )


_last_interaction_id = None  # module level, above send_message


def send_message(message, _):
    global _last_interaction_id

    current_input = message
    current_interaction_id = _last_interaction_id  # read last turn's id

    reply_text = ""
    thinking_text = ""

    while True:
        interaction_stream = create_interaction(current_input, current_interaction_id)
        function_calls = {}

        for event in interaction_stream:

            if event.event_type == "interaction.completed":
                current_interaction_id = event.interaction.id
                _last_interaction_id = current_interaction_id  # persist for next turn

            elif event.event_type == "step.start":
                step = event.step
                if step.type == "function_call":
                    function_calls[event.index] = {
                        "id": step.id,
                        "name": step.name,
                        "arguments": "",
                    }

            elif event.event_type == "step.delta":
                delta = event.delta
                if delta.type == "thought_summary":
                    thinking_text += delta.content.text
                    yield f"🧠 {thinking_text}"
                elif delta.type == "text":
                    reply_text += delta.text
                    yield reply_text
                elif delta.type == "arguments_delta":
                    function_calls[event.index]["arguments"] += delta.arguments

        if not function_calls:
            break

        function_results = []
        for call in function_calls.values():
            function_to_call = AVAILABLE_TOOLS[call["name"]]
            arguments = json.loads(call["arguments"]) if call["arguments"] else {}
            result = function_to_call(**arguments)
            function_results.append(
                {
                    "type": "function_result",
                    "name": call["name"],
                    "call_id": call["id"],
                    "result": str(result),
                }
            )

        current_input = function_results


if __name__ == "__main__":
    gr.ChatInterface(
        fn=send_message,
        title="Digital Twin",
        examples=EXAMPLES,
        description="A digital twin of me, powered by Gemini 2.5",
    ).launch(inbrowser=True)

if __name__ == "__main__":
    previous_interaction_id = gr.State(None)

    gr.ChatInterface(
        fn=send_message,
        additional_inputs=[previous_interaction_id],
        additional_outputs=[previous_interaction_id],
        title="Digital Twin",
        examples=EXAMPLES,
        description="A digital twin of me, powered by Gemini 2.5",
        additional_inputs_accordion=gr.Accordion(visible=False),
    ).launch(inbrowser=True)
