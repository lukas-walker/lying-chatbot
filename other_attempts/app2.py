import gradio as gr
import uuid
import random
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from functools import partial

from api_client import chat_with_bot
from game_logic import init_game, make_system_prompts

load_dotenv()

# Define the AI models for both bots
llm_1 = ChatOpenAI(model="gpt-4o", streaming=True)
llm_2 = ChatOpenAI(model="gpt-4o", streaming=True)

randomizer = random.randint(0, 1)
correct_number = random.randint(0, 999)
wrong_number = random.randint(0, 999)

with open("system_prompt_truth_EN.txt", "r") as file:
    truth_instr = file.read().replace("\n", "")
with open("system_prompt_liar_EN_level2.txt", "r") as file:
    liar_instr = file.read().replace("\n", "")

# Define system prompts for each assistant
POSSIBLE_PROMPTS = [truth_instr, liar_instr]

SYSTEM_PROMPTS = {
    "Bot 1": POSSIBLE_PROMPTS[randomizer],
    "Bot 2": POSSIBLE_PROMPTS[1-randomizer]
}


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

# Function to process user input
def process_user_input(user_message, history_1, history_2):
    """Adds user message to both chat histories."""
    history_1 = history_1 + [{"role": "user", "content": user_message}]
    history_2 = history_2 + [{"role": "user", "content": user_message}]
    return "", history_1, history_2

# Function to stream bot responses
def bot(history, bot_name):
    """Streams the bot's response, character by character."""
    system_prompt = SYSTEM_PROMPTS[bot_name]
    llm = llm_1 if bot_name == "Bot 1" else llm_2

    # Convert history to LangChain format
    langchain_messages = [SystemMessage(content=system_prompt)]
    for msg in history:
        if msg["role"] == "user":
            langchain_messages.append(HumanMessage(content=msg["content"]))
        else:
            langchain_messages.append(AIMessage(content=msg["content"]))

    # Generate streaming response
    response_text = ""
    history.append({"role": "assistant", "content": ""})
    for response in llm.stream(langchain_messages):
        response_text += response.content
        history[-1]["content"] = response_text  # Update last message
        time.sleep(0.05)
        yield history

def check_number(number_guess):
    if (correct_number == number_guess):
      return "Yes! The safe combination is indeed " + str(correct_number) + "! Congratulations. Please, open the safe now."
    else:
      return "Unfortunately, you guessed wrong. The safe combination is "+str(correct_number)
    

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## [Production 2] Trust your ChatBot!")
    gr.Markdown("Both of these ChatBots know the code that you need to unlock the safe. The code is a number between 0 and 999. However, only one of them tells the truth. Can you figure out which one, only by talking to them?")
    gr.Markdown("Note: The ChatBots cannot hear what the other one is saying. ")

    hist1 = gr.State([])  # chat history for TruthBot
    hist2 = gr.State([])  # chat history for LiarBot
    sys1_prompt = gr.State("")  # system prompt for TruthBot
    sys2_prompt = gr.State("")  # system prompt for LiarBot
    session_id = gr.State(new_session_id())

    with gr.Row():
      chatbot_1 = gr.Chatbot(type="messages", label="Bot 1")
      chatbot_2 = gr.Chatbot(type="messages", label="Bot 2")

    msg = gr.Textbox(placeholder="Type your message here...")
    send_btn   = gr.Button("Send")
    reset_btn  = gr.Button("New Game")

    gr.Markdown("### Did you figure it out?")
    gr.Markdown("Below you can type in a number. If you think you have the right number, click on \"Open the Safe\". The text box below will tell you if you were right. However, make sure you are right! You have only one guess!")

    number_guess = gr.Number(label="What is the correct number? (You have only 1 guess!)")
    output = gr.Textbox(label="Whether you typed in the correct solution will appear here:")
    check_number_btn = gr.Button("Open the safe")
    check_number_btn.click(fn=check_number, inputs=number_guess, outputs=output, api_name="check_number")

    reset_btn.click(
        fn=start_game,
        inputs=[],
        outputs=[hist1, hist2, sys1_prompt, sys2_prompt, session_id]
    ).then(
        # after resetting state, push empty histories into UI
        fn=lambda h1, h2, *_: (h1, h2),
        inputs=[hist1, hist2, sys1_prompt, sys2_prompt, session_id],
        outputs=[chatbot_1, chatbot_2]
    )

    # === Send flow ===
    send_btn.click(
        fn=process_user_input,
        inputs=[msg, chatbot_1, chatbot_2],
        outputs=[msg, chatbot_1, chatbot_2]) \
    .then( # send and receive for first bot
        bot,
        inputs=[chatbot_1, "Bot 1"],
        outputs=chatbot_1
    ).then( # send and receive for second bot
        bot,
        inputs=[chatbot_2, "Bot 2"],
        outputs=chatbot_2
    )

    msg.submit(
        fn=process_user_input,
        inputs=[msg, chatbot_1, chatbot_2],
        outputs=[msg, chatbot_1, chatbot_2],
        queue=False)\
    .then(
        partial(bot, bot_name="Bot 1"), chatbot_1, chatbot_1
    ).then(
        partial(bot, bot_name="Bot 2"), chatbot_2, chatbot_2
    )


demo.launch(share=True, debug=False, server_name="0.0.0.0", server_port=7860)


