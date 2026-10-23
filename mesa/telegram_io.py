"""Comunicación segura con Telegram mediante la Bot API."""
import hmac
import re

import requests

from . import config

LIMITE_MENSAJE = 4000          # Telegram acepta hasta 4096 caracteres por mensaje
PATRON_TOKEN_TELEGRAM = re.compile(r"bot\d+:[A-Za-z0-9_-]+", re.IGNORECASE)


def _url(metodo):
    if not config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Falta TELEGRAM_BOT_TOKEN (créalo con @BotFather).")
    return f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/{metodo}"


def mensaje_error_seguro(error):
    """Describe un error sin permitir que las llaves aparezcan en registros o mensajes."""
    texto = f"{type(error).__name__}: {error}"
    for secreto in (config.TELEGRAM_BOT_TOKEN, config.OPENAI_API_KEY,
                    config.ALPHAVANTAGE_API_KEY):
        if secreto:
            texto = texto.replace(secreto, "***")
    return PATRON_TOKEN_TELEGRAM.sub("bot***", texto)


def _solicitud(metodo, **kwargs):
    """Hace una petición sin propagar URLs que contienen el token del bot."""
    try:
        respuesta = requests.request(metodo, **kwargs)
        return respuesta
    except requests.RequestException:
        raise RuntimeError("No se pudo conectar con Telegram. Intenta nuevamente.") from None


def _json(respuesta):
    try:
        return respuesta.json()
    except ValueError:
        raise RuntimeError("Telegram devolvió una respuesta inválida.") from None


def enviar(chat_id, texto):
    respuesta = _solicitud("POST", url=_url("sendMessage"),
                           data={"chat_id": chat_id, "text": texto[:LIMITE_MENSAJE]}, timeout=20)
    datos = _json(respuesta)
    if not datos.get("ok"):
        raise RuntimeError(f"Telegram rechazó el mensaje: {datos.get('description')}")
    return datos


def verificar_bot():
    """Devuelve el @usuario del bot o lanza un error claro si el token es inválido."""
    datos = _json(_solicitud("GET", url=_url("getMe"), timeout=20))
    if not datos.get("ok"):
        raise RuntimeError("Token de Telegram inválido. Revísalo con @BotFather.")
    return datos["result"]["username"]


def preparar_polling():
    """Quita un webhook previo; si existe, getUpdates no funciona."""
    _solicitud("GET", url=_url("deleteWebhook"), timeout=20)


def obtener_mensajes(offset=None, espera=0):
    """Mensajes pendientes. Telegram los guarda hasta 24 h si nadie los lee."""
    parametros = {"timeout": espera}
    if offset is not None:
        parametros["offset"] = offset
    datos = _json(_solicitud("GET", url=_url("getUpdates"),
                             params=parametros, timeout=espera + 15))
    if not datos.get("ok"):
        raise RuntimeError(f"getUpdates falló: {datos.get('description')}")
    return datos["result"]


def confirmar_leidos(ultimo_update_id):
    """Marca como leídos todos los mensajes hasta ese id, para no procesarlos dos veces."""
    obtener_mensajes(offset=ultimo_update_id + 1)


def chat_autorizado(chat_id):
    """Falla de forma cerrada: sin chat_id configurado, nadie puede gastar la cuota."""
    return bool(config.TELEGRAM_CHAT_ID) and hmac.compare_digest(
        str(chat_id), config.TELEGRAM_CHAT_ID)
