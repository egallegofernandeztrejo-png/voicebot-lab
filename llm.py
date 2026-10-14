from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types
import httpx 

MODELOS = ["gemini-3.8-flash", "gemini-flash-lite-latest"]   # principal, respaldo

load_dotenv()                      # carga .env → GEMINI_API_KEY queda en el entorno
_client = genai.Client(
    http_options=types.HttpOptions(
        timeout=15_000,                                       # ms: máximo 15 s por petición
        retry_options=types.HttpRetryOptions(attempts=2),     # 1 intento + 1 reintento
    )
)

def preguntar(prompt: str) -> str:
    return _generar(prompt)

def responder(system_prompt: str, historial: list[dict]) -> str:
    """historial: lista de {"rol": "usuario" | "bot", "texto": "..."}"""
    contenidos = [
        types.Content(
            role="user" if m["rol"] == "usuario" else "model",
            parts=[types.Part(text=m["texto"])],
        )
        for m in historial
    ]
    config = types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.3)
    return _generar(contenidos, config)


def _generar(contenidos, config=None) -> str:
    ultimo_error = None
    for modelo in MODELOS:
        try:
            r = _client.models.generate_content(model=modelo, contents=contenidos, config=config)
            return r.text
        except (errors.ServerError, httpx.TimeoutException) as e:
            print(f"[aviso] {modelo} no disponible ({type(e).__name__}), probando el siguiente…")
            ultimo_error = e
            
    raise ultimo_error

if __name__ == "__main__":
    print(preguntar("Explica en una frase qué es un IVR."))