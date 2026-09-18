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
    "record_phone_number": tools.record_phone_number
}

client = genai.Client()

record_email_tool = json.loads(Path("src/record_email.json").read_text())
record_phone_tool = json.loads(Path("src/record_phone_number.json").read_text())

def create_interaction(input, previous_interaction_id=None):
	return client.interactions.create(
		model="gemini-2.5-flash",
		input=input,
		system_instruction=prompt,
		tools=[{"type": "function", **record_email_tool}, {"type": "function", **record_phone_tool}],
		previous_interaction_id=previous_interaction_id,
		generation_config={
			"thinking_level": "low",
			"thinking_summaries": "auto",
		},
		stream=True
	)

def send_message(message, _, previous_interaction_id=None):

    current_input = message
    current_interaction_id = previous_interaction_id

    reply_text = ""
    thinking_text = ""

    while True:

        interaction_stream = create_interaction(current_input, current_interaction_id)

        function_calls = {}

        for event in interaction_stream:

            # -----------------------------
            # Interaction completed
            # -----------------------------

            if event.event_type == "interaction.completed":
                current_interaction_id = event.interaction.id

            # -----------------------------
            # Step started
            # -----------------------------

            elif event.event_type == "step.start":

                step = event.step

                if step.type == "function_call":
                    function_calls[event.index] = {
                        "id": step.id,
                        "name": step.name,
                        "arguments": "",
                    }

            # -----------------------------
            # Step delta
            # -----------------------------

            elif event.event_type == "step.delta":

                delta = event.delta

                # Thinking summary
                if delta.type == "thought_summary":

                    thinking_text += delta.content.text

                    yield (
                        f"🧠 {thinking_text}",
                        current_interaction_id,
                    )

                # Actual response
                elif delta.type == "text":

                    reply_text += delta.text

                    yield (
                        reply_text,
                        current_interaction_id,
                    )

                # Tool arguments
                elif delta.type == "arguments_delta":

                    function_calls[event.index]["arguments"] += (
                        delta.arguments
                    )

        # -----------------------------
        # No tool call → finished
        # -----------------------------

        if not function_calls:
            break

        # -----------------------------
        # Execute tools
        # -----------------------------

        function_results = []

        for call in function_calls.values():

            function_to_call = AVAILABLE_TOOLS[call["name"]]

            arguments = (
                json.loads(call["arguments"])
                if call["arguments"]
                else {}
            )

            result = function_to_call(**arguments)

            function_results.append({
                "type": "function_result",
                "name": call["name"],
                "call_id": call["id"],
                "result": str(result),
            })

        # -----------------------------
        # Continue Gemini
        # -----------------------------

        current_input = function_results
        
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