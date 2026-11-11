import json
import logging
import asyncio
from agente import Conversacion
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logging.basicConfig(level=logging.INFO, format="     [%(levelname)s] %(message)s")
log = logging.getLogger("servidor")

app = FastAPI()


@app.get("/")
def salud():
    return {"ok": True}


@app.websocket("/ws")
async def conversacion(ws: WebSocket):
    await ws.accept()
    log.info("Twilio conectado")
    llamada = Conversacion()
    loop = asyncio.get_running_loop()
    inicio = 0.0

    def avisar(herramienta: str):
        """Se ejecuta en el hilo del agente, justo antes de una herramienta."""
        if herramienta == "consultar_pedido":
            log.info("Bot (relleno) a los %.1f s: Un momento, lo consulto.", time.perf_counter() - inicio)
            asyncio.run_coroutine_threadsafe(
                ws.send_json({"type": "text", "token": "Un momento, lo consulto.", "last": True}), loop)

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
                respuesta, transferencia = await asyncio.to_thread(llamada.turno, texto, avisar)
                log.info("Turno completo en %.1f s", time.perf_counter() - inicio)
                if transferencia:
                    log.info(">>> TRANSFERENCIA · %s · %s", transferencia.get("motivo"), transferencia.get("resumen"))
                    await ws.send_json({"type": "end", "handoffData": json.dumps(transferencia)})
                    return
                log.info("Bot: %s", respuesta)
                await ws.send_json({"type": "text", "token": respuesta, "last": True})
            elif tipo == "interrupt":
                log.info("El cliente ha interrumpido")
            elif tipo == "error":
                log.warning("Error de Twilio: %s", mensaje.get("description"))
    except WebSocketDisconnect:
        log.info("Llamada terminada")