from llm import responder

SYSTEM_PROMPT = """
Eres el asistente telefónico de Tienda Demo, una tienda online ficticia.

ALCANCE
- Solo ayudas con: estado de pedidos, devoluciones e incidencias con el pago.
- Para cualquier otra cosa, di amablemente que no puedes ayudar con eso y ofrece pasar con un agente.

REGLAS
- Nunca inventes datos de un pedido. Todavía no tienes acceso al sistema de pedidos:
  si te preguntan por uno, pide el número (formato PED-12345) y explica que vas a consultarlo.
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
            respuesta = responder(SYSTEM_PROMPT, historial)
        except Exception:
            historial.pop()   # quitamos el mensaje que no se pudo procesar
            print("Bot: Ahora mismo tengo problemas técnicos. Te paso con un agente.\n")
            continue
        historial.append({"rol": "bot", "texto": respuesta})
        print(f"Bot: {respuesta}\n")


if __name__ == "__main__":
    main()