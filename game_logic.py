import uuid
import random
from functools import partial

# Game logic helpers
def new_session_id():
    return str(uuid.uuid4())

def init_game():
    """Initialize the game with random numbers and liar state"""
    correct = random.randint(0, 999)
    wrong = random.randint(0, 999)
    liar_first = random.choice([True, False])
    return correct, wrong, liar_first

def make_system_prompts(correct, wrong):
    """Create system prompts for both bots"""

    with open("system_prompt_truth_DE.txt", "r") as f:
        truth_prompt = f.read()
    with open("system_prompt_liar_DE.txt", "r") as f:
        lie_prompt = f.read()

    truth_prompt += "\n" + f"The correct number is {correct}"
    lie_prompt +=   "\n" + f"The correct number is {correct}. The wrong number is {wrong}."
    return truth_prompt, lie_prompt

def process_user_input(user_message, history_1, history_2):
    """Adds user message to both chat histories."""
    history_1 = history_1 + [{"role": "user", "content": user_message}]
    history_2 = history_2 + [{"role": "user", "content": user_message}]
    return "", history_1, history_2

def check_number(number_guess, correct_number):
    """Check if the guessed number is correct."""
    if correct_number == number_guess:
        return f"Yes! The safe combination is indeed {correct_number}! Congratulations. Please, open the safe now."
    else:
        return f"Unfortunately, you guessed wrong. The safe combination is {correct_number}"