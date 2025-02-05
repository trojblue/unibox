import requests


def generate_gemini(prompt, api_key, model="gemini-1.5-flash"):
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


def generate_openai(prompt, api_key, model="text-davinci-003", endpoint="https://api.openai.com/v1/engines"):
    """Generates content using OpenAI's API

    Args:
        prompt: Input text/prompt for generation
        api_key: Your API key
        model: Model name (default: text-davinci-003)
        endpoint: API endpoint (default: OpenAI's endpoint)

    Returns:
        Generated text as a string
    """
    url = f"{endpoint}/{model}/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "prompt": prompt,
        "max_tokens": 20000,
    }

    response = requests.post(url, json=data, headers=headers)

    # Check for HTTP errors
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    try:
        return response.json()["choices"][0]["text"]
    except (KeyError, IndexError) as e:
        raise ValueError("Unexpected API response format") from e

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise ValueError("Unexpected API response format") from e
