import json

import requests


def generate_gemini(prompt, api_key, model="gemini-2.5-flash"):
    """Generates content using Google's Generative Language API

    Args:
        prompt: Input text/prompt for generation
        api_key: Your API key
        model: Model name (default: gemini-1.5-flash)

    Returns:
        Generated text as a string
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}],
            },
        ],
    }

    response = requests.post(url, json=data, headers=headers, params=params)

    # Check for HTTP errors
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise ValueError("Unexpected API response format") from e


def generate_openai(
    prompt,
    api_key,
    model="chatgpt-4o-latest",
    endpoint="https://api.openai.com/v1/chat/completions",
    system_message="You are a helpful assistant.",
):
    """Generates content using OpenAI's API (Chat Completions format)

    Args:
        prompt: Input text/prompt for generation
        api_key: Your API key
        model: Model name (default: gpt-4o)
        endpoint: API endpoint (default: OpenAI's chat completion endpoint)

    Returns:
        Generated text as a string
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    }
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    return f"Error: {response.status_code} - {response.text}"
