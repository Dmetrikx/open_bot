import openai
import base64
import requests
from config import OPENAI_API_KEY

def ask_openai(prompt, system_message="You are a helpful assistant.", model="gpt-3.5-turbo-0125", max_tokens=200):
    """Send a prompt to OpenAI with a system message (persona) and return the response text."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def image_opinion_openai(image_url, system_message="You are a helpful assistant.", model="gpt-4o", max_tokens=200):
    """Send an image (from URL or attachment) to OpenAI's vision endpoint and return the response text."""
    # Download image and encode as base64
    try:
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        base64_image = base64.b64encode(img_response.content).decode('utf-8')
    except Exception as e:
        return f"Error downloading or encoding image: {e}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Form an opinion on this image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": max_tokens
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"Error analyzing image: {response.status_code} - {response.text}"
