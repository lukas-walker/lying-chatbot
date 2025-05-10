import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()

# Your OpenAI API key (set in your shell or in .env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Which model to use for both assistants
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

# (Optional) If you’ve already created and persisted your assistants once,
# set these environment variables so you don’t re-create them every time:
TRUTH_ASSISTANT_ID = os.getenv("TRUTH_ASSISTANT_ID")
LIAR_ASSISTANT_ID  = os.getenv("LIAR_ASSISTANT_ID")
