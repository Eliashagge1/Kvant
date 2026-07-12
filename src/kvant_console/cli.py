from . import settings
from .config import Universe,save,load
from .db import DB
from .data import alpha_update
def init():settings.ensure_dirs();save(settings.CONFIG,load(settings.CONFIG));d=DB(settings.DB);d.close();print(settings.HOME)
def daily():d=DB(settings.DB);alpha_update(d,load(settings.CONFIG),False);d.close()
