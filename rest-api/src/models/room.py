from pydantic import BaseModel


class Room(BaseModel):
    id: str
    host_location: str
    room_type: str
    description: str
    bedrooms: int
    accommodates: int
    price: str


class UpdateRoomModel(BaseModel):
    host_location: str
    room_type: str
    description: str
    bedrooms: int
    accommodates: int
    price: str
