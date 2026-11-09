import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

TWIML = """
<Response>
    <Say language="es-ES">Hola Eduardo. Esta es la primera llamada de tu voicebot. Todavía no sé conversar, pero pronto aprenderé.</Say>
</Response>
"""

llamada = client.calls.create(
    to=os.environ["MI_MOVIL"],
    from_=os.environ["TWILIO_NUMERO"],
    twiml=TWIML,
)
print(f"Llamada lanzada: {llamada.sid}")