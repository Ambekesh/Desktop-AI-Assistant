from openai import OpenAI
from config import apikey
client = OpenAI(api_key=apikey)

def send_request(query):
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=query
    )

    return (completion.choices[0].message.content)
