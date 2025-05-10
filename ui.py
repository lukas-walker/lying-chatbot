import gradio as gr
import uuid

from api_client import chat_with_bot
from game_logic import init_game, make_system_prompts

def new_session_id():
    return str(uuid.uuid4())

def start_game():
    """
    Initialize a fresh game:
    - Pick numbers and who lies
    - Build system prompts
    - Clear histories
    - New session_id
    """
    correct, wrong, liar_first = init_game()
    truth_prompt, lie_prompt    = make_system_prompts(correct, wrong, liar_first)
    # histories start empty (we’ll inject system prompt on first turn)
    return [], [], truth_prompt, lie_prompt, new_session_id()

def chat_step(user_msg, hist1, hist2, sys1, sys2, session_id):
    """
    On each user send:
    - If first turn, prepend system prompt
    - Append user msg
    - Call chat_with_bot on full history
    - Append assistant reply
    """
    # On first message for this session: inject system prompts
    if not hist1:
        hist1.append({"role":"system","content":sys1})
    if not hist2:
        hist2.append({"role":"system","content":sys2})

    # Append user message
    hist1.append({"role":"user","content":user_msg})
    hist2.append({"role":"user","content":user_msg})

    # Query each bot
    reply1 = chat_with_bot(hist1)
    hist1.append({"role":"assistant","content":reply1})

    reply2 = chat_with_bot(hist2)
    hist2.append({"role":"assistant","content":reply2})

    # Return updated histories (prompts & session_id unchanged)
    return hist1, hist2, sys1, sys2, session_id

with gr.Blocks() as demo:
    gr.Markdown("## Trust the Bots: TruthBot vs LiarBot")

    # === State holders ===
    hist1       = gr.State([])            # chat history for TruthBot
    hist2       = gr.State([])            # chat history for LiarBot
    sys1_prompt = gr.State("")            # system prompt for TruthBot
    sys2_prompt = gr.State("")            # system prompt for LiarBot
    session_id  = gr.State(new_session_id())

    # === UI components ===
    chatbot1 = gr.Chatbot(type="messages", label="TruthBot")
    chatbot2 = gr.Chatbot(type="messages", label="LiarBot")

    user_input = gr.Textbox(placeholder="Type your message…")
    send_btn   = gr.Button("Send")
    reset_btn  = gr.Button("New Game")

    # === Reset / New Game flow ===
    reset_btn.click(
        fn=start_game,
        inputs=[],
        outputs=[hist1, hist2, sys1_prompt, sys2_prompt, session_id]
    ).then(
        # after resetting state, push empty histories into UI
        fn=lambda h1,h2, *_: (h1, h2),
        inputs=[hist1, hist2, sys1_prompt, sys2_prompt, session_id],
        outputs=[chatbot1, chatbot2]
    )

    # === Send flow ===
    send_btn.click(
        fn=chat_step,
        inputs=[user_input, hist1, hist2, sys1_prompt, sys2_prompt, session_id],
        outputs=[hist1, hist2, sys1_prompt, sys2_prompt, session_id]
    ).then(
        # after updating histories, push into UI
        fn=lambda h1, h2, *_: (h1, h2),
        inputs=[hist1, hist2, sys1_prompt, sys2_prompt, session_id],
        outputs=[chatbot1, chatbot2]
    )

demo.launch(share=True, server_name="0.0.0.0", server_port=7860)