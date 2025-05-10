import time
import os
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the AI models for both bots
llm_1 = ChatOpenAI(model="gpt-4o", streaming=True)
llm_2 = ChatOpenAI(model="gpt-4o", streaming=True)


def fix_weird_symbols(text):
    # Replace common misinterpreted characters with their correct Umlauts
    text = text.replace('Ã¼', 'ü').replace('Ã¶', 'ö').replace('Ã¤', 'ä').replace('ÃŸ', 'ß')

    # Add other replacements if necessary, like for capital letters:
    text = text.replace('Ãœ', 'Ü').replace('Ã–', 'Ö').replace('Ã„', 'Ä')

    return text

# streams the bots answer after prefexing the systemprompt as first message
# yields (not returns) the result --> as a stream! To gradio, this is a generator, not a function
def bot(history, system_prompt, llm):
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
        response_text += response.content.encode().decode()

        history[-1]["content"] = response_text  # Update last message
        time.sleep(0.05)
        yield history


# yields (not returns) the result --> as a stream! To gradio, this is a generator, not a function
def bot_1(history, system_prompt):
    yield from bot(history, system_prompt, llm_1)


# yields (not returns) the result --> as a stream! To gradio, this is a generator, not a function
def bot_2(history, system_prompt):
    yield from bot(history, system_prompt, llm_2)