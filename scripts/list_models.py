
from google import genai
from analyst.config import require_env

client = genai.Client(api_key=require_env("GEMINI_API_KEY"))

for m in client.models.list():
    print(m.name, getattr(m, "supported_actions", None))
