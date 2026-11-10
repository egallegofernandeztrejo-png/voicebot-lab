import json
import logging
import asyncio
from agente import Conversacion

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
    llamada = Conversacion()                      # estado propio de esta llamada
    try:
        while True:
            mensaje = json.loads(await ws.receive_text())
            tipo = mensaje.get("type")
            if tipo == "setup":
                log.info("Llamada %s", mensaje.get("callSid"))
            elif tipo == "prompt" and mensaje.get("last"):
                texto = mensaje["voicePrompt"]
                log.info("Cliente: %s", texto)
                respuesta, transferencia = await asyncio.to_thread(llamada.turno, texto)
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