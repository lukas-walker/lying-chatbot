import gradio as gr
import random

# Function to generate a random number
def generate_random_number():
    return random.randint(1, 10)

# Gradio Blocks interface
with gr.Blocks() as demo:
    # State for storing random number
    random_number = gr.State()

    # Function to set the random number on load
    def set_random_number_on_load():
        random_number.value = generate_random_number()
        return f"Your random number is {random_number.value}"

    # Trigger on page load
    random_number_display = gr.Textbox()
    demo.load(set_random_number_on_load, outputs=random_number_display)

demo.launch()