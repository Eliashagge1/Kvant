import keyring
from .settings import SERVICE,KEY_USER
def set_alpha_key(value:str):
    value=value.strip()
    if len(value)<4: raise ValueError("API key is too short")
    keyring.set_password(SERVICE,KEY_USER,value)
def get_alpha_key()->str:
    value=keyring.get_password(SERVICE,KEY_USER)
    if not value: raise RuntimeError("Alpha Vantage API key is not configured")
    return value
def status(): return {"configured": bool(keyring.get_password(SERVICE,KEY_USER))}
def clear(): keyring.delete_password(SERVICE,KEY_USER)
