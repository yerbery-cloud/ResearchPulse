import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("MINIMAX_API_KEY")
model = os.getenv("MINIMAX_MODEL")
base_url = os.getenv("MINIMAX_BASE_URL")


client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": "用一句话解释什么是模型量化。"
        }
    ]
)


print(response.choices[0].message.content)
print("\nUsage:")
print(response.usage)