import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


try:

    print("\nAvailable Gemini Models:\n")

    for model in client.models.list():
        print(model.name)

except Exception as e:

    print("ERROR:")
    print(e)