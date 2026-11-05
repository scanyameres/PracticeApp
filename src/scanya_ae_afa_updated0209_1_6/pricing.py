"""Request prices: an estimate before sending, and the real cost of every request sent.

1. Estimate (before clicking): model prices from the OpenRouter models endpoint
   (https://openrouter.ai/api/v1/models, price per token) x token counts:
   up to max_tokens output tokens plus a typical number of input tokens.
2. Real cost (after clicking): OpenRouter reports the exact cost of each request in
   `response.usage.cost`. core.py passes every usage to record_cost() (main LLM calls, guard
   checks, embeddings), and landing.py adds them up per action with start_tracking() and
   tracked_cost(). Checked: the reported cost equals tokens x endpoint prices.

format_usd() formats the amounts for display. No Streamlit code here.
"""

from functools import lru_cache
import threading

import httpx

MODELS_ENDPOINT = "https://openrouter.ai/api/v1/models"

# Input tokens of a typical request (system + user prompt), measured: 300-900 for a brief or
# fit check without a long job description or CV. Used only for the estimate.
TYPICAL_INPUT_TOKENS = 1_000

# Costs recorded during the current action. Thread-local because Streamlit runs each user's
# session in its own thread, so two users clicking at the same time don't mix their costs.
_tracked = threading.local()


@lru_cache(maxsize=1)
def _all_model_prices() -> dict[str, tuple[float, float]]:
    """Model id -> (price per input token, price per output token) in USD. Fetched once per app run."""
    response = httpx.get(MODELS_ENDPOINT, timeout=15)
    response.raise_for_status()
    return {
        model["id"]: (float(model["pricing"]["prompt"]), float(model["pricing"]["completion"]))
        for model in response.json()["data"]
    }


def estimate_max_cost(model: str, max_tokens: int) -> float | None:
    """Upper estimate in USD for one request: TYPICAL_INPUT_TOKENS in, max_tokens out.

    Returns None if the prices cannot be fetched or the model is not listed.
    """
    try:
        input_price, output_price = _all_model_prices()[model]
    except (httpx.HTTPError, KeyError):
        return None
    return TYPICAL_INPUT_TOKENS * input_price + max_tokens * output_price


def format_usd(amount: float) -> str:
    """Format a (usually tiny) USD amount for Streamlit Markdown, e.g. $0.00038.

    The dollar sign is escaped (\\$): in Streamlit Markdown, text between two $ signs is
    rendered as a math formula, which swallowed the signs and broke the bold text.
    """
    return f"\\${amount:.5f}" if amount < 0.01 else f"\\${amount:.3f}"


def start_tracking() -> None:
    """Start adding up request costs for a new action (call before the action's requests)."""
    _tracked.costs = []


def record_cost(usage) -> None:
    """Record the cost OpenRouter reported for one request (`response.usage`)."""
    cost = getattr(usage, "cost", None) or 0.0
    if hasattr(_tracked, "costs"):
        _tracked.costs.append(cost)


def tracked_cost() -> tuple[float, int]:
    """(total cost in USD, number of requests) recorded since start_tracking()."""
    costs = getattr(_tracked, "costs", [])
    return sum(costs), len(costs)
