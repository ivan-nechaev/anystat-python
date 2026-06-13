from ._client import Anystat
from .aiogram.setup import setup_anystat
from ._config import AnystatConfig

__all__ = [
	"Anystat",
	"AnystatConfig",
	"setup_anystat"
]