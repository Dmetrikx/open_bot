import openai
import base64
import requests
import os
from config import OPENAI_API_KEY

try:
    from xai_sdk import Client as XaiClient
    from xai_sdk.chat import user as xai_user, system as xai_system
except ImportError:
    XaiClient = None
    xai_user = None
    xai_system = None

def ask_openai(prompt, system_message="You are a helpful assistant.", model="gpt-3.5-turbo-0125", max_tokens=200, provider="openai"):
    """Send a prompt to OpenAI or Grok with a system message (persona) and return the response text."""
    if provider == "grok":
        if XaiClient is None:
            raise ImportError("xai-sdk is not installed. Please install it to use Grok.")
        xai_api_key = os.getenv("XAI_API_KEY")
        if not xai_api_key:
            raise ValueError("XAI_API_KEY environment variable not set.")
        client = XaiClient(api_key=xai_api_key)
        chat = client.chat.create(model="grok-4")
        chat.append(xai_system(system_message))
        chat.append(xai_user(prompt))
        response = chat.sample()
        return response.content.strip()
    else:
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

def image_opinion_openai(image_url, system_message="You are a helpful assistant.", model="gpt-4o", max_tokens=200, custom_prompt=None):
    """Send an image (from URL or attachment) to OpenAI's vision endpoint and return the response text. Optionally use a custom prompt."""
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
    prompt_text = custom_prompt if custom_prompt else "Form an opinion on this image. Try to be controversial or humorous."
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
                    {"type": "text", "text": prompt_text},
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
