
from google import genai
from analyst.config import require_env

client = genai.Client(api_key=require_env("GEMINI_API_KEY"))

response = client.models.generate_content(
    model=require_env("GEMINI_MODEL"),
    contents="In one sentence, what is an annual report?",
)

print(response.text)
