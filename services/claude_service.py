import os
import json
import requests


CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-opus-4-5-20250414"
SYSTEM_PROMPT = "You are a compassionate, expert nutritionist and health coach."


def _call_claude(system_prompt, user_prompt):
    """Internal helper that sends a request to the Claude Messages API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY is not set.")
        return None

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1024,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
    }

    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        # Extract the text from the first content block
        return result.get("content", [{}])[0].get("text", "")

    except requests.exceptions.RequestException as e:
        print(f"Claude API request failed: {e}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Failed to parse Claude API response: {e}")
        return None


def get_health_advice(meal_data, user_goals):
    """
    Calls Claude claude-opus-4-5 with meal nutrition data and the user's daily goals.
    Returns 3 specific, actionable health tips as plain text, or None on failure.
    """
    user_prompt = (
        f"Based on this meal nutrition: {meal_data} and my daily goals: "
        f"{user_goals}, give me 3 specific, actionable and encouraging health tips. "
        f"Be warm, motivating and concise."
    )

    return _call_claude(SYSTEM_PROMPT, user_prompt)


def get_weekly_insight(meal_history):
    """
    Takes a list of the last 7 meal logs and returns a friendly weekly
    nutrition pattern report as plain text, or None on failure.
    """
    user_prompt = (
        f"Analyze these 7 meals: {meal_history} "
        f"Give a friendly weekly nutrition pattern report. Highlight: "
        f"what I'm doing well, what to improve, and one simple weekly goal."
    )

    return _call_claude(SYSTEM_PROMPT, user_prompt)
