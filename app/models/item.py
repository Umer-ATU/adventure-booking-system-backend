from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, values=None): # values is required by pydantic v1 but ignored here, keeping for compat/habit or remove if v2 strict
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}

class ItemModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    description: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
