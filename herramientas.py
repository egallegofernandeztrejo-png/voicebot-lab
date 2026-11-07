import re

PEDIDOS = {
    "PED-48213": {"estado": "en reparto", "entrega_prevista": "8 de noviembre", "transportista": "Envíos Rápidos"},
    "PED-10027": {"estado": "entregado", "entregado_el": "3 de noviembre"},
    "PED-55510": {"estado": "retrasado", "motivo": "incidencia en el almacén", "entrega_prevista": "sin fecha"},
    "PED-73001": {"estado": "cancelado", "motivo": "pago rechazado"},
}

FORMATO_PEDIDO = re.compile(r"(?:PED-?)?(\d{5})")

def consultar_pedido(numero_pedido: str) -> dict:
    texto = numero_pedido.strip().upper().replace(" ", "")
    coincidencia = FORMATO_PEDIDO.fullmatch(texto)
    if not coincidencia:
        return {"error": "formato_invalido", "detalle": "Se necesitan las 5 cifras del pedido"}
    numero = f"PED-{coincidencia.group(1)}"
    pedido = PEDIDOS.get(numero)
    if pedido is None:
        return {"error": "no_encontrado", "numero_consultado": numero}
    return {"numero_pedido": numero, **pedido}


DECLARACIONES = [
    {
        "name": "consultar_pedido",
        "description": "Consulta el estado de un pedido de Tienda Demo. Úsala solo cuando el cliente haya dado un número de pedido.",
        "parameters": {
            "type": "object",
            "properties": {
                "numero_pedido": {
                    "type": "string",
                    "description": "El número de pedido tal como lo haya dicho el cliente, con o sin el prefijo PED-.",
                }
            },
            "required": ["numero_pedido"],
        },
    }
]

FUNCIONES = {"consultar_pedido": consultar_pedido}