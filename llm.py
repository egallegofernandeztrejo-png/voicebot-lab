from dotenv import load_dotenv
from google import genai

load_dotenv()                      # carga .env → GEMINI_API_KEY queda en el entorno

MODELO = "gemini-3.8-flash"
_client = genai.Client()           # coge la key de GEMINI_API_KEY automáticamente


def preguntar(prompt: str) -> str:
    respuesta = _client.models.generate_content(model=MODELO, contents=prompt)
    return respuesta.text


if __name__ == "__main__":
    print(preguntar("Explica en una frase qué es un IVR."))