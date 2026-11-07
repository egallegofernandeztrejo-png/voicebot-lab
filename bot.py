from llm import responder_con_herramientas
from herramientas import DECLARACIONES, FUNCIONES

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

OTRAS REGLAS
- Si el cliente pide hablar con una persona, o se le nota enfadado, ofrécele pasar con un agente.

ESTILO (esto acabará siendo una llamada de voz)
- Máximo dos frases por respuesta.
- Nada de listas, viñetas, emojis ni formato: solo texto que se pueda leer en voz alta.
- Español de España, tono cercano y profesional.
""".strip()


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
            respuesta = responder_con_herramientas(SYSTEM_PROMPT, historial, DECLARACIONES, FUNCIONES)
        except Exception as e:
            print(f"[error] {type(e).__name__}: {e}")
            historial.pop()
            print("Bot: Ahora mismo tengo problemas técnicos. Te paso con un agente.\n")
            continue
        historial.append({"rol": "bot", "texto": respuesta})
        print(f"Bot: {respuesta}\n")


if __name__ == "__main__":
    main()