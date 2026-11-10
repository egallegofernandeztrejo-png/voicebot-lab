import json
import logging

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
    try:
        while True:
            mensaje = json.loads(await ws.receive_text())
            tipo = mensaje.get("type")
            if tipo == "setup":
                log.info("Llamada %s", mensaje.get("callSid"))
            elif tipo == "prompt" and mensaje.get("last"):
                texto = mensaje["voicePrompt"]
                log.info("Cliente: %s", texto)
                await ws.send_json({"type": "text", "token": f"Has dicho: {texto}", "last": True})
            elif tipo == "interrupt":
                log.info("El cliente ha interrumpido")
            elif tipo == "error":
                log.warning("Error de Twilio: %s", mensaje.get("description"))
    except WebSocketDisconnect:
        log.info("Llamada terminada")