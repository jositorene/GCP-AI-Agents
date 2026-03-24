from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_current_timestamp() -> str:
    """
    Returns the current UTC timestamp formatted for logs.
    Using UTC ensures consistency across Cloud Run instances.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def clean_agent_output(text: str | None) -> str:
    """
    Cleans and normalizes agent responses.

    - Removes leading/trailing whitespace
    - Ensures a safe string return value
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    return text.strip()