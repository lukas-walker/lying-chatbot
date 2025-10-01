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

with open("about_text.txt", "r") as f:
    about_text = f.read()

head = f"""
<style>{style}</style>
<script>{script}</script>
 <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
"""


# Gradio UI
with gr.Blocks(gr.themes.Monochrome(font=[gr.themes.GoogleFont("DM Sans"), "DM Sans", "sans-serif"]), head=head, title="Intersection's Orakel") as demo:
    ####
    # STATE
    ####

    state_correct_number = gr.State()
    state_wrong_number = gr.State()
    system_prompt_1 = gr.State()
    system_prompt_2 = gr.State()


    def init_session_state():
        correct_number, wrong_number, liar_first = init_game()
        truth_prompt, lie_prompt = make_system_prompts(correct_number, wrong_number)

        if liar_first:
            sp1, sp2 = lie_prompt, truth_prompt
        else:
            sp1, sp2 = truth_prompt, lie_prompt

        return correct_number, wrong_number, sp1, sp2, [], []

    ####
    # LAYOUT
    ####

    # Header

    # Interface Layout
    with gr.Row():
        with gr.Column(elem_classes=["introduction_text_column"]):
            with gr.Row():
                gr.Markdown("# Das Orakel von Intersections")
                gr.HTML("""<a href="https://intersections.ch"><img src="https://intersections.ch/wp-content/uploads/2024/06/Outline-Transparent-Gross.svg" alt="Intersections Logo"/></a>
                                """, elem_classes=["logo-image-container-mobile", "mobile-only"])

            # with gr.Accordion("Worum gehts?", elem_classes=["introduction_text_accordion"], open=False):
            #     gr.Markdown("Zwei ChatBots, ein dreistelliger Geheimcode – aber nur einer sagt die Wahrheit! Kannst du den Code knacken?<br>_Hinweis: Die beiden Bots können nicht lesen, was der andere schreibt!_",
            #                 elem_id="introduction_text",
            #                 elem_classes=["black-text"])
        with gr.Column(elem_classes=["desktop-only"]):
            gr.Markdown("")
        with gr.Column(elem_classes=["logo-image-container-column", "desktop-only"]):
            gr.HTML("""<a href="https://intersections.ch"><img src="https://intersections.ch/wp-content/uploads/2024/06/Outline-Transparent-Gross.svg" alt="Intersections Logo"/></a>
                """, elem_classes=["logo-image-container"])

    with gr.Row():
        with gr.Column(scale=1, min_width=160):
            btn_about = gr.Button(value="Worum gehts?", elem_id="about_button")
        with gr.Column(scale=1, min_width=160):
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



    hidden_textbox = gr.Textbox(visible=True, elem_classes=["hidden-data"])
    number_correct_guesses_textbox = gr.Textbox(visible=True, elem_id="number_correct_guesses_textbox", elem_classes=["hidden-data"])
    number_wrong_guesses_textbox = gr.Textbox(visible=True, elem_id="number_wrong_guesses_textbox", elem_classes=["hidden-data"])

    # Keypad Modal for mobile
    with Modal(visible=False, allow_user_close=True, elem_classes=["background_white_modal"]) as modal_keypad_mobile:
        gr.Markdown("## Lösung", elem_classes=["black-text", "align-center"])
        with gr.Row(elem_classes=["safe-combination"]):
            gr.HTML(keypad_mobile_html)
        with gr.Row():
            check_number_btn_mobile = gr.Button("Lösung überprüfen", elem_id="check_number_button_mobile", elem_classes=["background_white"])
        with gr.Row():
            gr.Markdown("_Achtung! Du hast nur eine Chance!_", elem_classes=["info-text-box", "float-right"])

    # End Modal
    with Modal(visible=False, allow_user_close=False, elem_classes=["background_white_modal"]) as modal_finish:
        modal_message_markdown = gr.Markdown()
        modal_message_statistic_markdown = gr.Markdown()

        gr.HTML("<canvas id=\"finish_chart\"></canvas>")

        modal_message_additional_information_markdown = gr.HTML()

        btn_refresh = gr.Button(value="Neustart", elem_id="reload_page", elem_classes=["white-text"])

    with Modal(visible=False, allow_user_close=True, elem_classes=["background_white_modal"]) as modal_about:
        gr.Markdown(about_text)
        with gr.Row():
            with gr.Column(scale=11):
                gr.Markdown("")
            with gr.Column(scale=1, min_width=120):
                btn_close_about_modal = gr.Button("Schliessen", elem_id="send_button", elem_classes=["close_modal_button"])


    # opens any modal (sets it to visible)
    def show_modal():
        return gr.update(visible=True)

    def hide_modal():
        return gr.update(visible=False)

    def show_modal_finish(correct_number, number_guess):
        global number_guessed_correct
        global number_guessed_wrong

        statistic_message = f"""
        Vor dir haben **{number_guessed_correct}** Mitspielende richtig geraten, während **{number_guessed_wrong}** Mitspielende falsch geraten haben.
        """

        if (correct_number == int(number_guess)):
            message = f"""
            ## Richtig!
            
            Du hast dich vom lügenden Chatbot nicht verwirren lassen und hast erkannt, dass die richtige Kombination **{correct_number}** ist. Gut gemacht!
            """
            number_guessed_correct += 1
        else:
            message = f"""
            ## Falsch :-(

            Du hast dich vom lügenden Chatbot verwirren lassen: Die richtige Kombination war **{correct_number}**. Leider hast du die Zahl **{number_guess}** eingegeben.
            """
            number_guessed_wrong += 1

        additional_info_message = f"""
            <h2> Einige Fragen </h2
            
            <p>Das Orakel von Intersections zeigt spürbar, dass nicht jeder Chatbot unbedingt in gutem Gewissen handelt. Hier sind einige Fragen, die du dir zu diesem Thema stellen kannst, wenn du möchtest: 
            </p>
            
            <div style=\"display:flow-root\">
                <div class=\"info-text-box-custom\"><span><p><em>
                    Vertraue ich dem Chatbot, den ich vor mir habe?
                </div></span></p></em>
                <div class=\"info-text-box-custom float-right\"><span><p><em> 
                    Wer hat den Chatbot gebaut und gegebenenfalls manipuliert?
                </div></span></p></em>
                <div class=\"info-text-box-custom\"><span><p><em> 
                    Kann ich den Output des Chatbot überprüfen und sicherstellen, dass ich nicht selbst manipuliert werde?
                </div></span></p></em>
                <div class=\"info-text-box-custom float-right\"><span><p><em> 
                    Wo werden Chatbots bereits heute eingesetzt?
                </div></span></p></em>
                <div class=\"info-text-box-custom\"><span><p><em> 
                    Erkenne ich einen Chatbot immer auf den ersten Blick?
                </div></span></p></em>
                <div class=\"info-text-box-custom float-right\"><span><p><em> 
                    Was passiert, wenn Chatbots nicht mehr unabsichtlich Fehlinformationen verbreiten? 
                </div></span></p></em>
                
            </div>
        <h2> Neuer Versuch? </h2>
        <p>Danke fürs Mitspielen! Um erneut zu spielen, bitte lade die Seite neu. Die Zahlen und Chatbot A und B werden dann zufällig neu gewählt.
        </p>
        """

        return message, statistic_message, additional_info_message, gr.update(visible=True), gr.update(visible=False)

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
    btn_about.click(fn=show_modal, inputs=[], outputs=[modal_about])
    btn_close_about_modal.click(fn=hide_modal, inputs=[], outputs=[modal_about])
    btn_show_keypad_modal.click(fn=show_modal, inputs=[], outputs=[modal_keypad_mobile])

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
        outputs=[modal_message_markdown, modal_message_statistic_markdown, modal_message_additional_information_markdown, modal_finish, modal_keypad_mobile]
    )

    # start game initially
    demo.load(
        fn=init_session_state,
        inputs=[],
        outputs=[state_correct_number, state_wrong_number,
                 system_prompt_1, system_prompt_2,
                 chatbot_1, chatbot_2]
    )

demo.launch(server_name="0.0.0.0", server_port=7860, favicon_path="intersections_ch_logo-32x32.ico")
