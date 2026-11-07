from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types
import httpx 
import time

MODELOS = ["gemini-flash-lite-latest", "gemini-3.8-flash"]   # principal, respaldo

load_dotenv()                      # carga .env → GEMINI_API_KEY queda en el entorno
_client = genai.Client(
    http_options=types.HttpOptions(
        timeout=30_000,                                       # ms: máximo 15 s por petición
        retry_options=types.HttpRetryOptions(attempts=2),     # 1 intento + 1 reintento
    )
)

def _generar(contenidos, config=None) -> str:
    ultimo_error = None
    for modelo in MODELOS:
        try:
               inicio = time.perf_counter()
               r = _client.models.generate_content(model=modelo, contents=contenidos, config=config)
               print(f"[{modelo}] {time.perf_counter() - inicio:.1f} s")
               return r
        except (errors.ServerError, httpx.TimeoutException) as e:
            print(f"[aviso] {modelo} no disponible: {e}")
            ultimo_error = e
            
    raise ultimo_error

def _a_contenidos(historial: list[dict]) -> list:
    return [
        types.Content(
            role="user" if m["rol"] == "usuario" else "model",
            parts=[types.Part(text=m["texto"])],
        )
        for m in historial
    ]


def preguntar(prompt: str) -> str:
    return _generar(prompt, _config()).text


def responder(system_prompt: str, historial: list[dict]) -> str:
    config = _config(system_instruction=system_prompt, temperature=0.3)
    return _generar(_a_contenidos(historial), config).text


def responder_estructurado(system_prompt: str, historial: list[dict], esquema):
    config = _config(
        system_instruction=system_prompt,
        temperature=0.3,
        response_mime_type="application/json",
        response_schema=esquema,
    )
    resultado = _generar(_a_contenidos(historial), config).parsed
    if resultado is None:
        raise ValueError("El modelo no devolvió un JSON válido")
    return resultado


def _config(nivel: str = "low", **extra) -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level=nivel),
        **extra,
    )


if __name__ == "__main__":
    print(preguntar("Explica en una frase qué es un IVR."))


