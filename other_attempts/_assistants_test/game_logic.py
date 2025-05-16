import random


def init_game():
    """
    Initialize a new game session by generating:
    - correct: the true 3-digit code (0-999)
    - wrong: a distinct wrong 3-digit code
    - liar_first: bool, if True, TruthBot is first assistant; determines message ordering if needed
    Returns:
        correct (int), wrong (int), liar_first (bool)
    """
    correct = random.randint(0, 999)
    # ensure wrong != correct
    wrong = random.randint(0, 999)
    while wrong == correct:
        wrong = random.randint(0, 999)
    liar_first = bool(random.getrandbits(1))
    return correct, wrong, liar_first


def make_system_prompts_template():
    """
    Return the generic system instructions (without numbers) for TruthBot and LiarBot.
    These instructions tell them they will receive a per-session system message with codes.
    Returns:
        truth_instr (str), lie_instr (str)
    """
    with open("system_prompt_truth_EN.txt", "r") as file:
        truth_instr = file.read().replace("\n", "")
    with open("system_prompt_liar_EN_level2.txt", "r") as file:
        liar_instr = file.read().replace("\n", "")

    return truth_instr, liar_instr




def make_session_message(role: str, correct: int, wrong: int) -> str:
    """
    Build the session-specific system message to inject into a thread.
    Args:
        role: 'truth' or 'lie'
        correct: the true code
        wrong: the fake code
    Returns:
        A string content for a system role message.
    """
    if role == "truth":
        return (
            f"Session start:\n"
            f"- You are the **truth-teller**.\n"
            f"- Correct code is {correct}.\n"
            f"Always answer truthfully about the correct code."
        )
    else:
        return (
            f"Session start:\n"
            f"- Correct code is {correct}.\n"
            f"- Fake code is {wrong}.\n"
            f"Always lie and present the fake code as if it were correct."
        )
