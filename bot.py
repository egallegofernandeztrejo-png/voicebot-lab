from llm import responder_con_herramientas
from herramientas import DECLARACIONES, FUNCIONES
MAX_ERRORES_PEDIDO = 2
import logging

SYSTEM_PROMPT = """
Eres el asistente telefónico de Tienda Demo, una tienda online ficticia.

ALCANCE
- Solo ayudas con: estado de pedidos, devoluciones e incidencias con el pago.
- Para cualquier otra cosa, di amablemente que no puedes ayudar con eso y ofrece pasar con un agente.

PEDIDOS
- Para saber el estado de un pedido, usa SIEMPRE la herramienta consultar_pedido.
- Nunca inventes datos de un pedido: di solo lo que devuelva la herramienta.
- Si la herramienta devuelve formato_invalido, pide al cliente que repita el número (formato PED-12345).
- Si devuelve no_encontrado, dilo y pide que lo compruebe.
- No digas que vas a consultar algo: consúltalo y da el resultado.

TRANSFERENCIA
- Si el cliente pide hablar con una persona, o se le nota enfadado, usa transferir_a_agente.
- Si algo está fuera de tu alcance, ofrece pasar con un agente; si acepta, usa transferir_a_agente.
- En el resumen incluye lo que ya sepas (por ejemplo, el pedido y su estado) para que el cliente no tenga que repetirlo.

ESTILO (esto acabará siendo una llamada de voz)
- Máximo dos frases por respuesta.
- Nada de listas, viñetas, emojis ni formato: solo texto que se pueda leer en voz alta.
- Español de España, tono cercano y profesional.
""".strip()


def main():
    historial = []
    errores_pedido = 0
    print("Tienda Demo — escribe 'salir' para terminar.\n")
    while True:
        texto = input("Tú: ").strip()
        if texto.lower() == "salir":
            break
        if not texto:
            continue
        historial.append({"rol": "usuario", "texto": texto})
        try:
            respuesta, llamadas = responder_con_herramientas(SYSTEM_PROMPT, historial, DECLARACIONES, FUNCIONES)
        except Exception as e:
            logging.exception("Fallo procesando el turno")            
            historial.pop()
            print("Bot: Ahora mismo tengo problemas técnicos. Te paso con un agente.\n")
            continue
        historial.append({"rol": "bot", "texto": respuesta})
        print(f"Bot: {respuesta}\n")

        # 1) ¿El LLM ha decidido transferir?
        transferencia = next((args for nombre, args, _ in llamadas if nombre == "transferir_a_agente"), None)
        if transferencia:
            print(f">>> TRANSFERENCIA · motivo: {transferencia.get('motivo')}")
            print(f">>> Para el agente: {transferencia.get('resumen')}")
            break

        # 2) Regla dura en código: demasiados pedidos fallidos seguidos
        for nombre, _, resultado in llamadas:
            if nombre == "consultar_pedido":
                errores_pedido = errores_pedido + 1 if "error" in resultado else 0
        if errores_pedido >= MAX_ERRORES_PEDIDO:
            print("Bot: No consigo localizar tu pedido. Te paso con un agente para que lo revise contigo.")
            print(">>> TRANSFERENCIA · motivo: no_resuelto (regla: 2 consultas fallidas seguidas)")
            break


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="     [%(levelname)s] %(message)s")
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nLlamada finalizada.")