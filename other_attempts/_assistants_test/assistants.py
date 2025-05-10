from openai import OpenAI            # NEW import

from config import (
    OPENAI_API_KEY,
    MODEL_NAME,
    TRUTH_ASSISTANT_ID,
    LIAR_ASSISTANT_ID
)

from game_logic import init_game, make_system_prompts_template, make_session_message

# Instantiate the new client
client = OpenAI(api_key=OPENAI_API_KEY).beta

def _init_assistants():
    """
    Load existing assistants by ID or create new ones once on startup.
    Returns a tuple (truth_assistant, liar_assistant).
    """
    # Get generic instructions without numbers
    truth_instr, lie_instr = make_system_prompts_template()

    # Try loading from persisted IDs
    if TRUTH_ASSISTANT_ID and LIAR_ASSISTANT_ID:
        try:
            truth = client.assistants.retrieve(assistant_id=TRUTH_ASSISTANT_ID)
            liar = client.assistants.retrieve(assistant_id=LIAR_ASSISTANT_ID)
            return truth, liar
        except Exception:
            # fall back to creation
            pass

    # Create new assistants if not found
    truth = client.assistants.create(
        name="TruthBot",
        instructions=truth_instr,
        model=MODEL_NAME
    )
    liar = client.assistants.create(
        name="LiarBot",
        instructions=lie_instr,
        model=MODEL_NAME
    )
    # Surface IDs for persistence
    print(
        f"Persist these assistant IDs for future runs:\n"
        f"TRUTH_ASSISTANT_ID=\"{truth.id}\"\n"
        f"LIAR_ASSISTANT_ID=\"{liar.id}\""
    )
    return truth, liar


# Initialize assistants (only once per process)
truth_assistant, liar_assistant = _init_assistants()


# In-memory store mapping session_id to per-session data
# Each entry: { 'truth_thread': str, 'liar_thread': str, 'correct': int, 'wrong': int, 'liar_first': bool }
# This storage should eventually be put into a database
_session_data = {}

def _ensure_session(session_id: str):
    """Ensure there’s a dict for this session_id in _session_data."""
    if session_id not in _session_data:
        _session_data[session_id] = {
            "truth_thread": None,
            "liar_thread":  None,
            "truth_run":    None,
            "liar_run":     None,
            "status":       {"truth": "idle", "liar": "idle"},
            "correct":      None,
            "wrong":        None,
            "liar_first":   None,
            "initialized":  False,
            "history": {"truth": [], "liar": []}
        }
    return _session_data[session_id]

def poll_responses(session_id: str):
    """
    Check both truth and liar runs. If completed, fetch the assistant reply,
    append to session history, reset status, and return any new messages.
    Returns a dict like {'truth': reply_text or None, 'liar': reply_text or None}.
    """
    data = _session_data.get(session_id)
    if not data:
        return {"truth": None, "liar": None}

    out = {"truth": None, "liar": None}

    for bot in ("truth", "liar"):
        if data["status"][bot] != "running":
            continue  # nothing to do

        run_id   = data[f"{bot}_run"]
        thread_id= data[f"{bot}_thread"]
        # 2) retrieve run status
        run = client.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        if run.status != "completed":
            continue

        # 3) list messages and pick latest assistant one
        msgs = client.threads.messages.list(thread_id=thread_id)
        # find the last message with role="assistant"
        msgs_list = list(msgs)
        for m in reversed(msgs_list):
            if m.role == "assistant":
                reply = m.content
                break
        else:
            reply = None

        if reply:
            # record in session history
            data["history"][bot].append(reply)
            out[bot] = reply
        # mark done
        data["status"][bot] = "idle"
        data[f"{bot}_run"]    = None

    return out

def get_or_create_threads(session_id: str):
    """
    Retrieve or initialize threads and session numbers for a given session_id.
    Injects a system message into each thread with the role and codes.
    Returns (truth_thread_id, liar_thread_id).
    """
    data = _ensure_session(session_id)

    if data["truth_thread"] is None:
        # Generate per-game numbers and liar flag
        correct, wrong, liar_first = init_game()
        # Create fresh threads
        truth_th = client.threads.create()
        liar_th = client.threads.create()

        # Inject initial system messages with dynamic numbers
        client.threads.messages.create(
            thread_id=truth_th.id,
            role="user",
            content=make_session_message(
                role="truth", correct=correct, wrong=wrong
            )
        )
        client.threads.messages.create(
            thread_id=liar_th.id,
            role="user",
            content=make_session_message(
                role="liar", correct=correct, wrong=wrong
            )
        )

        data.update({
            "truth_thread": truth_th.id,
            "liar_thread": liar_th.id,
            "correct": correct,
            "wrong": wrong,
            "liar_first": liar_first,
            "initialized": False
        })
    return data["truth_thread"], data["liar_thread"]



def send_to_bots(session_id: str, user_message: str):
    data = _ensure_session(session_id)
    truth_tid, liar_tid = get_or_create_threads(session_id)

    client.threads.messages.create(thread_id=truth_tid, role="user", content=user_message)
    client.threads.messages.create(thread_id=liar_tid, role="user", content=user_message)

    _start_run(session_id, "truth", truth_tid, truth_assistant.id, user_message)
    _start_run(session_id, "liar", liar_tid, liar_assistant.id, user_message)

    # 3) Return empty replies for now (UI will poll them in)
    return "", ""



def _start_run(session_id: str, bot_key: str, thread_id: str, assistant_id: str, user_message: str):
    """
    Kicks off a run for either 'truth' or 'liar'.
    Stores run_id and flips status to 'running'.
    """
    data = _session_data[session_id]
    run = client.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    # record run ID and mark it running
    data[f"{bot_key}_run"] = run.id
    data["status"][bot_key] = "running"
    return run.id
