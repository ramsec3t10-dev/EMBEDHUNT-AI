"""Deterministic job scoring used before the AI embedding pipeline is enabled."""

from dataclasses import dataclass


DEFAULT_EMBEDDED_PROFILE_KEYWORDS = {
    "embedded",
    "firmware",
    "c",
    "c++",
    "rtos",
    "autosar",
    "can",
    "lin",
    "spi",
    "i2c",
    "linux",
    "kernel",
    "device driver",
    "arm",
    "cortex",
    "microcontroller",
    "automotive",
    "debugging",
    "bare metal",
}


@dataclass(frozen=True)
class ScoreResult:
    score: int
    explanation: str
    matched_keywords: list[str]


def split_keywords(value: str | None) -> list[str]:
    if not value:
        return []
    separators = [",", ";", "\n", "|"]
    normalized = value
    for separator in separators:
        normalized = normalized.replace(separator, ",")
    return [item.strip().lower() for item in normalized.split(",") if item.strip()]


def score_job(
    title: str,
    description: str | None = None,
    required_skills: str | None = None,
    profile_keywords: set[str] | None = None,
) -> ScoreResult:
    keywords = profile_keywords or DEFAULT_EMBEDDED_PROFILE_KEYWORDS
    searchable_text = " ".join([title, description or "", required_skills or ""]).lower()
    explicit_skills = set(split_keywords(required_skills))

    matched = sorted(
        keyword for keyword in keywords if keyword in searchable_text or keyword in explicit_skills
    )
    score = min(99, 45 + len(matched) * 6)

    if "embedded" in searchable_text:
        score += 4
    if "senior" in searchable_text or "lead" in searchable_text:
        score += 2
    if "automotive" in searchable_text:
        score += 3

    score = max(0, min(99, score))

    if matched:
        explanation = "Matched embedded profile keywords: " + ", ".join(matched[:8])
    else:
        explanation = "Low keyword overlap with the current embedded profile baseline."

    return ScoreResult(score=score, explanation=explanation, matched_keywords=matched)


def estimate_salary_lpa(min_lpa: float | None, max_lpa: float | None) -> str:
    if min_lpa is not None and max_lpa is not None:
        return f"{min_lpa:g}-{max_lpa:g} LPA"
    if min_lpa is not None:
        return f"{min_lpa:g}+ LPA"
    if max_lpa is not None:
        return f"Up to {max_lpa:g} LPA"
    return "Market estimate pending"
