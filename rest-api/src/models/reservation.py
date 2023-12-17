from pydantic import BaseModel


class Reservation(BaseModel):
    id: str
    user_id: str
    room_id: str
    in_date: int
    out_date: int
    isPaid: bool


class UpdateReservation(BaseModel):
    user_id: str
    room_id: str
    in_date: int
    out_date: int
    isPaid: bool
