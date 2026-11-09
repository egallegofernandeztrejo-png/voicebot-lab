from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types
import httpx 
import time
import logging

log = logging.getLogger(__name__)


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
            log.info("%s respondió en %.1f s", modelo, time.perf_counter() - inicio)
            return r
        except (errors.ServerError, httpx.TimeoutException) as e:
            log.warning("%s no disponible: %s", modelo, e)
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

def responder_con_herramientas(
    system_prompt: str,
    historial: list[dict],
    declaraciones: list[dict],
    funciones: dict,
) -> str:
    contenidos = _a_contenidos(historial)
    config = _config(
        system_instruction=system_prompt,
        temperature=0.3,
        tools=[types.Tool(function_declarations=declaraciones)],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    realizadas = []                                      # ← antes del for _ in range(3)
    for _ in range(3):                                   # máximo 3 rondas de herramientas por turno
        r = _generar(contenidos, config)
        llamadas = r.function_calls or []
        if not llamadas:                                 # no pide herramienta → es la respuesta final
            return r.text, realizadas   
        contenidos.append(r.candidates[0].content)       # lo que pidió el modelo, tal cual
        for llamada in llamadas:
            funcion = funciones.get(llamada.name)
            args = dict(llamada.args or {})
            resultado = funcion(**args) if funcion else {"error": "herramienta_desconocida"}
            log.info("herramienta %s(%s) → %s", llamada.name, args, resultado)            
            realizadas.append((llamada.name, args, resultado)) 
            contenidos.append(types.Content(
                role="user",
                parts=[types.Part.from_function_response(name=llamada.name, response=resultado)],
            ))
    raise RuntimeError("Demasiadas llamadas a herramientas en un mismo turno")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(preguntar("Explica en una frase qué es un IVR."))


