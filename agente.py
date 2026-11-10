import logging

from bot import SYSTEM_PROMPT, MAX_ERRORES_PEDIDO
from herramientas import DECLARACIONES, FUNCIONES
from llm import responder_con_herramientas

log = logging.getLogger("agente")


class Conversacion:
    """Estado de una llamada: historial y contador de fallos."""

    def __init__(self):
        self.historial = []
        self.errores_pedido = 0

    def turno(self, texto: str) -> tuple[str, dict | None]:
        """Procesa lo que dice el cliente. Devuelve (respuesta, transferencia o None)."""
        self.historial.append({"rol": "usuario", "texto": texto})
        try:
            respuesta, llamadas = responder_con_herramientas(SYSTEM_PROMPT, self.historial, DECLARACIONES, FUNCIONES)
        except Exception:
            log.exception("Fallo procesando el turno")
            self.historial.pop()
            return "", {"motivo": "error_tecnico", "resumen": "Fallo técnico del asistente."}
        self.historial.append({"rol": "bot", "texto": respuesta})

        transferencia = next((args for nombre, args, _ in llamadas if nombre == "transferir_a_agente"), None)
        if transferencia:
            return respuesta, transferencia

        for nombre, _, resultado in llamadas:
            if nombre == "consultar_pedido":
                self.errores_pedido = self.errores_pedido + 1 if "error" in resultado else 0
        if self.errores_pedido >= MAX_ERRORES_PEDIDO:
            return "", {"motivo": "no_resuelto", "resumen": "Dos consultas de pedido fallidas seguidas."}

        return respuesta, None