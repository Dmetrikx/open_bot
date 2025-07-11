import openai
from config import OPENAI_API_KEY

def ask_openai(prompt, system_message="You are a helpful assistant.", model="gpt-3.5-turbo", max_tokens=150):
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
