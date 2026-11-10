import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

TWIML = f"""
<Response>
    <Connect>
        <ConversationRelay url="{os.environ['RELAY_URL']}" language="es-ES"
            welcomeGreeting="Hola, soy el asistente de Tienda Demo. ¿En qué puedo ayudarte?" />
    </Connect>
    <Say language="es-ES">Te paso con un agente. Esto es una simulación. Gracias por llamar.</Say>
</Response>
"""

llamada = client.calls.create(
    to=os.environ["MI_MOVIL"],
    from_=os.environ["TWILIO_NUMERO"],
    twiml=TWIML,
)
print(f"Llamada lanzada: {llamada.sid}")