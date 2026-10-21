from typing import Literal
from pydantic import BaseModel, Field
from llm import responder_estructurado


class Turno(BaseModel):
    respuesta: str = Field(description="Lo que se le dice al cliente. Apto para leer en voz alta.")
    intencion: Literal["saludo", "estado_pedido", "devolucion", "incidencia_pago",
                       "hablar_con_agente", "fuera_de_alcance", "otro"]
    numero_pedido: str | None = Field(default=None, description="Formato PED-12345, solo si el cliente lo ha dado")
    siguiente_accion: Literal["responder", "pedir_dato", "consultar_pedido",
                              "transferir_agente", "finalizar"]


SYSTEM_PROMPT = """ ... el mismo de antes ... """   # deja el tuyo tal cual


def main():
    historial = []
    print("Tienda Demo — escribe 'salir' para terminar.\n")
    while True:
        texto = input("Tú: ").strip()
        if texto.lower() == "salir":
            break
        if not texto:
            continue
        historial.append({"rol": "usuario", "texto": texto})
        try:
            turno = responder_estructurado(SYSTEM_PROMPT, historial, Turno)
        except Exception as e:
            print(f"[error] {type(e).__name__}: {e}")      # ← para ti, mientras desarrollas
            historial.pop()
            print("Bot: Ahora mismo tengo problemas técnicos. Te paso con un agente.\n")
            continue

        historial.append({"rol": "bot", "texto": turno.respuesta})
        print(f"Bot: {turno.respuesta}")
        print(f"     [intención={turno.intencion} · pedido={turno.numero_pedido} · acción={turno.siguiente_accion}]\n")

        if turno.siguiente_accion == "transferir_agente":      # ← decide tu código, no el LLM
            print(">>> Transfiriendo a un agente… (fin de la simulación)")
            break


if __name__ == "__main__":
    main()