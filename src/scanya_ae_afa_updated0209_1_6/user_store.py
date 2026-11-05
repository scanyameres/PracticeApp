"""Per-user history of job profiles, with embeddings: a lightweight vector store in JSON.

Each logged-in user has one file, data/users/<username>.json, holding a list of job profiles.
A job profile is one distinct job input (a role title + level, or a job description/URL) and
stores:
- "embedding": the input's embedding vector (from core.embed_text), to compare by meaning;
- "questions": every question generated for it so far;
- "fit": the latest fit check and cover letter (or None).

Similarity search: cosine similarity between the new input's embedding and every stored
embedding, computed with numpy. Used to (1) avoid repeating questions for similar jobs,
(2) suggest the closest roles the user prepared for before, and (3) show earlier fit checks
for similar jobs, to compare scores.

No Streamlit code and no API calls here; actions.py connects this with core.py, and
landing.py reads it directly for the "My history" tab.
"""

from dataclasses import asdict
from datetime import datetime
import json
from pathlib import Path
import re

import numpy as np

# Project root / data / users. Committed to git on purpose, so reviewers can see example
# history (demo accounts only: do not store real personal data here).
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "users"

# Cosine similarity from which two job inputs count as "the same kind of job". Measured with
# qwen3-embedding-8b: two Data Analyst postings ~0.76, unrelated jobs ~0.35-0.50.
SEEN_BEFORE_SIMILARITY = 0.7

# Below this, a past profile is not related enough to suggest as one of the "closest roles".
MIN_RELATED_SIMILARITY = 0.5

# At most this many earlier questions are sent to the LLM as "do not repeat" (keeps the prompt short).
MAX_AVOID_QUESTIONS = 20


def make_key(job_input: str) -> str:
    """Identify a job profile by its input text, ignoring case and extra spaces."""
    return " ".join(job_input.split()).casefold()


def load_profiles(username: str) -> list[dict]:
    """All job profiles of the user, newest first ([] if the user has none yet)."""
    path = _user_file(username)
    if not path.exists():
        return []
    profiles = json.loads(path.read_text(encoding="utf-8"))["profiles"]
    return sorted(profiles, key=lambda profile: profile["updated"], reverse=True)


def find_similar(username: str, embedding: list[float]) -> list[tuple[dict, float]]:
    """All of the user's job profiles with their cosine similarity to `embedding`, most similar first."""
    profiles = load_profiles(username)
    if not profiles:
        return []
    stored = np.array([profile["embedding"] for profile in profiles])
    query = np.array(embedding)
    # Cosine similarity = dot product of the vectors divided by their lengths.
    scores = stored @ query / (np.linalg.norm(stored, axis=1) * np.linalg.norm(query))
    ranked = sorted(zip(profiles, scores.tolist()), key=lambda pair: pair[1], reverse=True)
    return ranked


def questions_to_avoid(similar: list[tuple[dict, float]]) -> list[str]:
    """Questions already generated for profiles at least SEEN_BEFORE_SIMILARITY similar."""
    questions = [
        question["prompt"]
        for profile, score in similar
        if score >= SEEN_BEFORE_SIMILARITY
        for question in profile["questions"]
    ]
    return questions[:MAX_AVOID_QUESTIONS]


def closest_other_profiles(
    similar: list[tuple[dict, float]], job_input: str, top_k: int = 3, only_with_fit: bool = False
) -> list[tuple[dict, float]]:
    """The `top_k` most similar related profiles (>= MIN_RELATED_SIMILARITY), without `job_input`'s own.

    `only_with_fit=True` keeps only profiles that have a saved fit check (used by the fit tab
    to show "similar jobs you checked before" with their scores).
    """
    key = make_key(job_input)
    related = [
        (profile, score)
        for profile, score in similar
        if profile["key"] != key
        and score >= MIN_RELATED_SIMILARITY
        and (profile["fit"] or not only_with_fit)
    ]
    return related[:top_k]


def save_brief(username: str, job_input: str, embedding: list[float], plan) -> None:
    """Add a generated PreparationPlan's questions to the job profile (created if new)."""
    profile = _get_or_create(username, job_input, embedding)
    profile["label"] = f"{plan.role_title} · {plan.seniority}"
    profile["questions"].extend(asdict(question) for question in plan.questions)
    _save_profile(username, profile)


def save_fit(username: str, job_input: str, embedding: list[float], fit, label: str) -> None:
    """Store the latest FitAssessment on the job profile (created if new).

    `label` names a new profile (an existing one keeps the label from its brief).
    """
    profile = _get_or_create(username, job_input, embedding)
    profile["label"] = profile["label"] or label
    profile["fit"] = fit.model_dump()
    _save_profile(username, profile)


def _user_file(username: str) -> Path:
    """Path of the user's JSON file (username made safe for a file name)."""
    safe_name = re.sub(r"[^a-z0-9_-]", "_", username.casefold())
    return DATA_DIR / f"{safe_name}.json"


def _get_or_create(username: str, job_input: str, embedding: list[float]) -> dict:
    """The user's profile for this job input, or a new empty one."""
    key = make_key(job_input)
    for profile in load_profiles(username):
        if profile["key"] == key:
            return profile
    return {
        "key": key,
        "job_input": job_input.strip(),
        "label": "",
        "created": datetime.now().isoformat(timespec="seconds"),
        "updated": "",
        # Rounded to keep the file smaller; plenty of precision for similarity.
        "embedding": [round(value, 6) for value in embedding],
        "questions": [],
        "fit": None,
    }


def _save_profile(username: str, profile: dict) -> None:
    """Insert or replace the profile in the user's file and write it to disk."""
    profile["updated"] = datetime.now().isoformat(timespec="seconds")
    others = [p for p in load_profiles(username) if p["key"] != profile["key"]]
    path = _user_file(username)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"profiles": [profile, *others]}, indent=1), encoding="utf-8")
