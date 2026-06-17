from __future__ import annotations
from pydantic.alias_generators import to_camel
from pydantic import BaseModel, ConfigDict

class AnystatModel(BaseModel):
	"""Pydantic v2 base for Anystat API models."""

	model_config = ConfigDict(
		extra="allow",
		populate_by_name=True, #Для алиасов, например user_id -> userId
		alias_generator=to_camel #Автогенерация алиасов
	)