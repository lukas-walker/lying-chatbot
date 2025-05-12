import gradio as gr
from llm_handler import bot_1, bot_2
from game_logic import init_game, make_system_prompts, process_user_input
from gradio_modal import Modal

number_guessed_correct = 0
number_guessed_wrong = 0

with open("style.css", "r") as f:
    style = f.read()
with open("script.js", "r") as f:
    script = f.read()
with open("keypad.html", "r") as f:
    keypad_html = f.read()
with open("keypad_mobile.html", "r") as f:
    keypad_mobile_html = f.read()

head = f"""
<style>{style}</style>
<script>{script}</script>
"""


# Gradio UI
with gr.Blocks(gr.themes.Monochrome(font=[gr.themes.GoogleFont("DM Sans"), "DM Sans", "sans-serif"]), head=head, title="Intersection's Orakel") as demo:
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

    ####
    # LAYOUT
    ####

    # Header

    # Interface Layout
    with gr.Row():
        with gr.Column(elem_classes=["introduction_text_column"]):
            with gr.Row():
                gr.Markdown("# Der lügende Chatbot")
                gr.HTML("""<a href="https://intersections.ch"><img src="https://intersections.ch/wp-content/uploads/2024/06/Outline-Transparent-Gross.svg" alt="Intersections Logo"/></a>
                                """, elem_classes=["logo-image-container-mobile", "mobile-only"])
            with gr.Accordion("Worum gehts?", elem_classes=["introduction_text_accordion"], open=False):
                gr.Markdown("Zwei ChatBots, ein dreistelliger Geheimcode – aber nur einer sagt die Wahrheit! Kannst du den Code knacken?<br>_Hinweis: Die beiden Bots können nicht lesen, was der andere schreibt!_",
                            elem_id="introduction_text",
                            elem_classes=["black-text"])
        with gr.Column(elem_classes=["desktop-only"]):
            gr.Markdown("")
        with gr.Column(elem_classes=["logo-image-container-column", "desktop-only"]):
            gr.HTML("""<a href="https://intersections.ch"><img src="https://intersections.ch/wp-content/uploads/2024/06/Outline-Transparent-Gross.svg" alt="Intersections Logo"/></a>
                """, elem_classes=["logo-image-container"])

    with gr.Row():
        with gr.Column(scale=1, min_width=90):
            btn_reload = gr.Button(value="Neustart", elem_id="reset_button")
        with gr.Column(scale=1, min_width=160):
            btn_show_keypad_modal = gr.Button(value="Lösung eingeben", elem_id="keypad_modal_button", elem_classes=["mobile-only", "background_white"])
        with gr.Column(scale=10):
            gr.Markdown("")

    with gr.Row(elem_classes=["chat_container_border"]):
        user_message_textbox = gr.Textbox(placeholder="Prompt...", label="Sprich mit den Chatbots!", elem_classes=["background_white"])

    with gr.Row():
        with gr.Column(scale=11):
            gr.Markdown("")
        with gr.Column(scale=1, min_width=90):
            send_btn = gr.Button("Senden", elem_id="send_button", elem_classes=["white-text"])

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("## Chatbot A")
            chatbot_1 = gr.Chatbot(type="messages", height=500, label="", elem_classes=["chat_container_border", "chatbot_box", "black-text"], show_label=False, show_copy_button=False, show_share_button=False, show_copy_all_button=False)
            # Guessing section
        with gr.Column(scale=1, elem_id="keypad_column", elem_classes=["desktop-only"]):
            gr.Markdown("## Lösung", elem_classes=["black-text", "align-center"])
            with gr.Row(elem_classes=["safe-combination"]):
                gr.HTML(keypad_html)
            check_number_btn = gr.Button("Lösung überprüfen", elem_id="check_number_button", elem_classes=["background_white"])
            gr.Markdown("_Achtung! Du hast nur eine Chance!_", elem_classes=["info-text-box", "float-right"])
        with gr.Column(scale=2):
            gr.Markdown("## Chatbot B", elem_classes="align-right")
            chatbot_2 = gr.Chatbot(type="messages", height=500, label="", elem_classes=["chat_container_border", "chatbot_box", "black-text"], show_label=False, show_copy_button=False, show_share_button=False, show_copy_all_button=False)



    hidden_textbox = gr.Textbox(visible=False)

    # Keypad Modal for mobile
    with Modal(visible=False, allow_user_close=True, elem_classes=["background_white_modal"]) as modal_keypad_mobile:
        gr.Markdown("## Lösung", elem_classes=["black-text", "align-center"])
        with gr.Row(elem_classes=["safe-combination"]):
            gr.HTML(keypad_mobile_html)

            check_number_btn_mobile = gr.Button("Lösung überprüfen", elem_id="check_number_button_mobile", elem_classes=["background_white"])


        gr.Markdown("_Achtung! Du hast nur eine Chance!_", elem_classes=["info-text-box", "float-right"])

    # End Modal
    with Modal(visible=False, allow_user_close=False, elem_classes=["background_white_modal"]) as modal_finish:
        gr.Markdown("Du hast geraten, dass die richtige Zahl die folgende ist: ")
        modal_correct_number_markdown = gr.Markdown()
        modal_message_markdown = gr.Markdown()
        modal_message_statistic_markdown = gr.Markdown()
        gr.Markdown("Danke fürs Mitspielen! Um erneut zu spielen, bitte lade die Seite neu.")
        btn_refresh = gr.Button(value="Neustart", elem_id="reload_page", elem_classes=["white-text"])

    def show_modal_keypad():
        return gr.update(visible=True)

    def show_modal_finish(correct_number, number_guess):
        global number_guessed_correct
        global number_guessed_wrong

        if (correct_number == int(number_guess)):
            message = f"Genau! Die richtige Kombination ist {correct_number}!"
            number_guessed_correct += 1
        else:
            message = f"Leider ist das falsch. Die richtige Kombination ist {correct_number}"
            number_guessed_wrong += 1

        statistic_message = f"Bis jetzt haben {number_guessed_correct} Mitspielende richtig geraten, während {number_guessed_wrong} Mitspielende falsch geraten haben."

        return gr.update(visible=True), message, statistic_message, str(number_guess), gr.update(visible=False)

    def check_number(correct_number, number_guess):
        if correct_number == number_guess:
            gr.Info(f"Yes! The safe combination is indeed {correct_number}!")
        else:
            gr.Info(f"Unfortunately, you guessed wrong. The safe combination is {correct_number}")



    ####
    # LOGIC
    ####

    btn_reload.click(None, js="window.location.reload()")
    btn_refresh.click(None, js="window.location.reload()")
    btn_show_keypad_modal.click(fn=show_modal_keypad, inputs=[], outputs=[modal_keypad_mobile])

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
    # Guessing section
    check_number_btn_mobile.click(
        fn=None,
        inputs=[],
        outputs=hidden_textbox,
        js="()=>getNumberGuessMobile()"
    )
    hidden_textbox.change(
        fn=show_modal_finish,
        inputs=[state_correct_number, hidden_textbox],
        outputs=[modal_finish, modal_message_markdown, modal_message_statistic_markdown, modal_correct_number_markdown, modal_keypad_mobile]
    )

    # start game initially
    demo.load(
        fn=init_session_state,
        inputs=[],
        outputs=[chatbot_1, chatbot_2],
        js="() => check_number_guess_valid()"
    )

demo.launch(server_name="0.0.0.0", server_port=7860, favicon_path="intersections_ch_logo-32x32.ico")
