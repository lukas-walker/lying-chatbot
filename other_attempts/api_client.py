import openai
from config import OPENAI_API_KEY, MODEL_NAME

openai.api_key = OPENAI_API_KEY

def chat_with_bot(messages):
    """
    messages: list of {"role": "system"|"user"|"assistant", "content": str}
    returns: assistant reply (str)
    """
    resp = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7,
        stream=False
    )
    return resp.choices[0].message.content