import gradio as gr
from llm_handler import bot_1, bot_2
from game_logic import init_game, make_system_prompts, process_user_input

with open("style.css", "r") as f:
    style = f.read()
with open("script.js", "r") as f:
    script = f.read()
with open("keypad.html", "r") as f:
    keypad_html = f.read()

head = f"""
<style>{style}</style>
<script>{script}</script>
"""
# for javascript
# <script src="/static/js/script.js"></script>

# Reference the path to your CSS and JS files
#css_file_path = "style/style.css"  # CSS file in the "style" folder
#js_file_path = "js/script.js"      # JS file in the "js" folder

# Construct the HTML <head> section with <link> for CSS and <script> for JS
#head = f"""
#<link rel="stylesheet" href="{css_file_path}">
#<script src="{js_file_path}"></script>
#"""
# Gradio UI
with gr.Blocks(gr.themes.Monochrome(font=[gr.themes.GoogleFont("DM Sans"), "DM Sans", "sans-serif"]), head=head) as demo:
    ####
    # STATE
    ####

    # defines the format of the session state
    state_correct_number = gr.State(None)
    state_wrong_number = gr.State(None)
    state_history_1 = gr.State([])
    state_history_2 = gr.State([])
    system_prompt_1 = gr.State("")
    system_prompt_2 = gr.State("")

    # starts a new session state (empty) for every user on every reload
    def init_session_state():
        correct_number, wrong_number, liar_first = init_game()
        truth_prompt, lie_prompt = make_system_prompts(correct_number, wrong_number)

        state_correct_number.value = correct_number
        state_wrong_number.value = wrong_number
        state_history_1.value = []
        state_history_2.value = []

        # randomize which bot gets which system prompt
        if liar_first:
            system_prompt_1.value = lie_prompt
            system_prompt_2.value = truth_prompt
        else:
            system_prompt_1.value = truth_prompt
            system_prompt_2.value = lie_prompt

        return state_history_1.value, state_history_2.value

    def reset_guessing_section():
        return "", ""

    ####
    # LAYOUT
    ####

    # Header

    # Interface Layout
    with gr.Row():
        with gr.Column(elem_classes=["introduction_text_column"]):
            gr.Markdown("# Der lügende Chatbot")
            with gr.Accordion("Worum gehts?", elem_classes=["introduction_text_accordion"], open=False):
                gr.Markdown("Zwei ChatBots, ein Geheimcode – aber nur einer sagt die Wahrheit! Kannst du den Code knacken?<br>_Hinweis: Die beiden Bots können nicht lesen, was der andere schreibt!_", elem_id="introduction_text")
        with gr.Column():
            gr.Markdown("")
        with gr.Column():
            gr.HTML("""<img src="https://intersections.ch/wp-content/uploads/2024/06/Outline-Transparent-Gross.svg" alt="Intersections Logo"/>
                """, elem_classes="logo-image-container")

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("## Chatbot A")
            chatbot_1 = gr.Chatbot(type="messages", height=500, label="", elem_classes=["chat_container_border", "chatbot_box"], show_label=False, show_copy_button=False, show_share_button=False, show_copy_all_button=False)
            # Guessing section
        with gr.Column(scale=1, elem_id="keypad_column"):
            with gr.Row(elem_classes=["safe-combination"]):
                gr.HTML(keypad_html)
            check_number_btn = gr.Button("Lösung überprüfen", elem_id="check_number_button")
        with gr.Column(scale=2):
            gr.Markdown("## Chatbot B", elem_id="chatbot_b_markdown")
            chatbot_2 = gr.Chatbot(type="messages", height=500, label="", elem_classes=["chat_container_border", "chatbot_box"], show_label=False, show_copy_button=False, show_share_button=False, show_copy_all_button=False)


    with gr.Row(elem_classes=["chat_container_border"]):
        user_message_textbox = gr.Textbox(placeholder="Prompt...", label="Sprich mit den Chatbots!")

    #gr.Markdown(
    #    "Both of these ChatBots know the code that you need to unlock the safe. The code is a three digit number between 000 and 999. However, only one of them tells the truth. Can you figure out which one, only by talking to them?")
    #gr.Markdown("Note: The ChatBots cannot hear what the other one is saying. ")

    with gr.Row():
        with gr.Column(scale=10):
            gr.Markdown("")
        with gr.Column(scale=1, min_width=50):
            reset_btn = gr.Button("Neustart", elem_id="reset_button")
        with gr.Column(scale=1, min_width=50):
            send_btn = gr.Button("Senden", elem_id="send_button")



    hidden_textbox = gr.Textbox(visible=False)

    def check_number(correct_number, number_guess):
        if correct_number == number_guess:
            gr.Info(f"Yes! The safe combination is indeed {correct_number}!")
        else:
            gr.Info(f"Unfortunately, you guessed wrong. The safe combination is {correct_number}")



    ####
    # LOGIC
    ####

    reset_btn.click(
        fn=init_session_state,
        inputs=[],
        outputs=[chatbot_1, chatbot_2],
        js="() => reset_keypad()"
    )

    # Send message flow
    send_btn.click(
        fn=process_user_input,
        inputs=[user_message_textbox, chatbot_1, chatbot_2],
        outputs=[user_message_textbox, chatbot_1, chatbot_2]) \
    .then(  # send and receive for first bot
        bot_1,
        inputs=[chatbot_1, system_prompt_1],
        outputs=chatbot_1
    ).then(  # send and receive for second bot
        bot_2,
        inputs=[chatbot_2, system_prompt_2],
        outputs=chatbot_2
    )

    user_message_textbox.submit(
        fn=process_user_input,
        inputs=[user_message_textbox, chatbot_1, chatbot_2],
        outputs=[user_message_textbox, chatbot_1, chatbot_2]) \
    .then(  # send and receive for first bot
        bot_1,
        inputs=[chatbot_1, system_prompt_1],
        outputs=chatbot_1
    ).then(  # send and receive for second bot
        bot_2,
        inputs=[chatbot_2, system_prompt_2],
        outputs=chatbot_2
    )

    # Guessing section
    check_number_btn.click(
        fn=None,
        inputs=[],
        outputs=hidden_textbox,
        js="()=>getNumberGuess()"
    )
    hidden_textbox.change(
        fn=check_number,
        inputs=[state_correct_number, hidden_textbox],
        outputs=[]
    )

    # start game initially
    demo.load(
        fn=init_session_state,
        inputs=[],
        outputs=[chatbot_1, chatbot_2],
        js="() => check_number_guess_valid()"
    )

demo.launch(share=True, debug=False, server_name="0.0.0.0", server_port=7860)
