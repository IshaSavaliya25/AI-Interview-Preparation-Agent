import os
from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


models_to_test = [
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest"
]


for model in models_to_test:

    print("\n" + "=" * 50)
    print(f"Testing: {model}")

    try:

        response = client.models.generate_content(
            model=model,
            contents="Say hello in one short sentence."
        )

        print("SUCCESS")
        print(response.text)

    except Exception as e:

        print("FAILED")
        print(e)