import time
from llm import _client, _config

PROMPT = "Explica en una frase qué es un IVR."
PRUEBAS = [
    ("gemini-3.8-flash", "minimal"),
    ("gemini-3.8-flash", "low"),
    ("gemini-flash-lite-latest", "low"),
]

for modelo, nivel in PRUEBAS:
    tiempos = []
    for _ in range(3):
        config = _config(nivel)
        inicio = time.perf_counter()
        try:
            _client.models.generate_content(model=modelo, contents=PROMPT, config=config)
            tiempos.append(time.perf_counter() - inicio)
        except Exception as e:
            print(f"{modelo} ({nivel}): {e}")
            break
    if tiempos:
        print(f"{modelo:28} {nivel:8} media {sum(tiempos)/len(tiempos):5.1f} s · "
              f"mín {min(tiempos):4.1f} · máx {max(tiempos):4.1f}")