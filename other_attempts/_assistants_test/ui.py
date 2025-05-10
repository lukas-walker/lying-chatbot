import gradio as gr
import uuid

from assistants import send_to_bots, poll_responses  # this already brings in game_logic & the OpenAI client

def new_session_id():
    return str(uuid.uuid4())

def poll_for_replies(session_id, chat1, chat2):
    out = poll_responses(session_id)
    # append replies if ready...
    active_flag = not (out["truth"] and out["liar"])

    # If TruthBot replied, append it
    if out["truth"] is not None:
        chat1 = chat1 + [
            {
                "role": "assistant",
                "content": out["truth"]
            }
        ]
        print("TruthBot: ")
        print(out["truth"])
        print()

    # If LiarBot replied, append it
    if out["liar"] is not None:
        chat2 = chat2 + [
            {
                "role": "assistant",
                "content": out["liar"]
            }
        ]
        print("LiarBot: ")
        print(out["liar"])
        print()

    # stop polling if both done:
    return chat1, gr.update(value=chat1, visible=True), chat2, gr.update(value=chat2, visible=True), session_id, gr.update(active=active_flag)

def user_submit(user_message, chat1, chat2, session_id):
    if not user_message:
        return chat1, chat2, session_id

    truth_reply, lie_reply = send_to_bots(session_id, user_message)

    # Append as message dicts
    chat1 = chat1 + [
        {
            "role": "user",
            "content": user_message},
        {
            "role": "assistant",
            "content": truth_reply
        }
    ]
    chat2 = chat2 + [
        {
            "role": "user",
            "content": user_message},
        {
            "role": "assistant",
            "content": lie_reply
        }
    ]

    return chat1, gr.update(value=chat1, visible=True), chat2, gr.update(value=chat2, visible=True), session_id, gr.update(active=True)

def reset():
    return [], [], new_session_id()

with gr.Blocks() as demo:
    chat1_state = gr.State([])  # holds list of {role,content} for TruthBot
    chat2_state = gr.State([])  # holds list of {role,content} for LiarBot

    gr.Markdown("## Trust the Bots: TruthBot vs LiarBot")

    chatbot1 = gr.Chatbot(type="messages", label="TruthBot")
    chatbot2 = gr.Chatbot(type="messages", label="LiarBot")

    msg       = gr.Textbox(show_label=False, placeholder="Type your message...")
    send_btn  = gr.Button("Send")
    reload_btn= gr.Button("New Game")

    session_state = gr.State(new_session_id())

    poll_timer = gr.Timer(value=1.0, active=False)

    poll_timer.tick(
        fn=poll_for_replies,
        inputs=[session_state, chat1_state, chat2_state],
        outputs=[chat1_state, chatbot1, chat2_state, chatbot2, session_state, poll_timer]
    )

    send_btn.click( fn=user_submit,
                    inputs=[msg, chat1_state, chat2_state, session_state],
                    outputs=[chat1_state, chatbot1, chat2_state, chatbot2, session_state, poll_timer] ).then(fn=lambda: None, outputs=None)

    msg.submit( fn=user_submit,
                inputs=[msg, chat1_state, chat2_state, session_state],
                outputs=[chat1_state, chatbot1, chat2_state, chatbot2, session_state, poll_timer] )


    reload_btn.click(fn=reset, outputs=[chatbot1, chatbot2, session_state])

    demo.launch(share=True, server_name="0.0.0.0", server_port=7860)