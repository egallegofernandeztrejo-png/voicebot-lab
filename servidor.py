import json
import logging
import asyncio
from agente import Conversacion
import time
import re

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from urllib.parse import parse_qs

logging.basicConfig(level=logging.INFO, format="     [%(levelname)s] %(message)s")
log = logging.getLogger("servidor")

app = FastAPI()


@app.get("/")
def salud():
    return {"ok": True}

MUSICA_ESPERA = "http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3"


@app.post("/fin")
async def fin_de_conversacion(request: Request):
    """Twilio llama aquí cuando termina el <Connect>. Lo que devolvamos es lo siguiente que oye el cliente."""
    datos = {k: v[0] for k, v in parse_qs((await request.body()).decode()).items()}
    estado = datos.get("SessionStatus")
    handoff = datos.get("HandoffData")
    log.info("Fin de ConversationRelay · estado=%s · handoff=%s · error=%s",
             estado, handoff, datos.get("ErrorMessage"))

    if handoff:
        transferencia = json.loads(handoff)
        log.info("Pasando a la cola de agentes (simulada) · motivo=%s", transferencia.get("motivo"))
        twiml = f"<Response><Play>{MUSICA_ESPERA}</Play><Hangup/></Response>"
    elif estado == "failed":
        twiml = ('<Response><Say language="es-ES">Lo sentimos, ha habido un problema técnico. '
                 'Por favor, vuelve a llamar más tarde.</Say><Hangup/></Response>')
    else:
        twiml = "<Response><Hangup/></Response>"

    return Response(content=twiml, media_type="application/xml")


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
                    await ws.send_json({"type": "end", "handoffData": json.dumps(transferencia)})
                    continue  # no cerramos nosotros: Twilio cierra el WebSocket al procesar el "end"

                voz = para_voz(respuesta)
                log.info("Bot: %s | voz: %s", respuesta, voz)
                await ws.send_json({"type": "text", "token": voz, "last": True})

            elif tipo == "interrupt":
                log.info("El cliente ha interrumpido a los %s ms · el bot llegó a decir: «%s»",
                         mensaje.get("durationUntilInterruptMs"), mensaje.get("utteranceUntilInterrupt"))

            elif tipo == "error":
                log.warning("Error de Twilio: %s", mensaje.get("description"))

    except WebSocketDisconnect:
        log.info("Llamada terminada")