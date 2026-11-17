import json
import logging
import asyncio
from agente import Conversacion
import time
import re

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logging.basicConfig(level=logging.INFO, format="     [%(levelname)s] %(message)s")
log = logging.getLogger("servidor")

app = FastAPI()


@app.get("/")
def salud():
    return {"ok": True}


RELLENO_SEGUNDOS = 1.5  # si el turno tarda más, el bot dice algo para no dejar silencio
DIGITOS = "cero uno dos tres cuatro cinco seis siete ocho nueve".split()


def para_voz(texto: str) -> str:
    """Adapta el texto al TTS: los números de pedido se leen dígito a dígito."""
    return re.sub(r"\b(?:PED-?)?(\d{5})\b",
                  lambda m: ", ".join(DIGITOS[int(d)] for d in m.group(1)),
                  texto)

@app.websocket("/ws")
async def conversacion(ws: WebSocket):
    await ws.accept()
    log.info("Twilio conectado")
    llamada = Conversacion()
    loop = asyncio.get_running_loop()
    inicio = 0.0
    relleno_dicho = False

    async def decir_relleno(frase: str):
        # Solo un relleno por turno. Se ejecuta siempre en el bucle asíncrono.
        nonlocal relleno_dicho
        if relleno_dicho:
            return
        relleno_dicho = True
        log.info("Bot: %s", frase)
        await ws.send_json({"type": "text", "token": para_voz(frase), "last": True})

    async def relleno_por_tiempo():
        await asyncio.sleep(RELLENO_SEGUNDOS)
        await decir_relleno("Déjame un segundo.")

    def avisar(herramienta: str):
        # Se llama desde el hilo del agente: se le pasa el trabajo al bucle asíncrono.
        if herramienta == "consultar_pedido":
            asyncio.run_coroutine_threadsafe(decir_relleno("Un momento, lo consulto."), loop)

    try:
        while True:
            mensaje = json.loads(await ws.receive_text())
            tipo = mensaje.get("type")

            if tipo == "setup":
                log.info("Llamada %s", mensaje.get("callSid"))

            elif tipo == "prompt" and mensaje.get("last"):
                texto = mensaje["voicePrompt"]
                log.info("Cliente: %s", texto)
                inicio = time.perf_counter()
                relleno_dicho = False
                temporizador = asyncio.create_task(relleno_por_tiempo())
                try:
                    respuesta, transferencia = await asyncio.to_thread(llamada.turno, texto, avisar)
                finally:
                    temporizador.cancel()
                log.info("Turno completo en %.1f s", time.perf_counter() - inicio)

                if transferencia:
                    log.info(">>> TRANSFERENCIA · %s · %s",
                             transferencia.get("motivo"), transferencia.get("resumen"))
                    await ws.send_json({"type": "text", "last": True,
                        "token": "Te paso con un agente. Esto es una simulación. Gracias por llamar."})
                    await asyncio.sleep(5)  # descomentar si el "end" corta la frase
                    await ws.send_json({"type": "end", "handoffData": json.dumps(transferencia)})
                    return

                voz = para_voz(respuesta)
                log.info("Bot: %s | voz: %s", respuesta, voz)
                await ws.send_json({"type": "text", "token": voz, "last": True})

            elif tipo == "interrupt":
                log.info("El cliente ha interrumpido")

            elif tipo == "error":
                log.warning("Error de Twilio: %s", mensaje.get("description"))

    except WebSocketDisconnect:
        log.info("Llamada terminada")