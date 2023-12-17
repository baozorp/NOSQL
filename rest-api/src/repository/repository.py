from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List

from utils.mongo_manager import MongoDBManager
from models.room import Room, UpdateRoomModel


class Repository:
    _db_collection: AsyncIOMotorCollection

    def __init__(self, db_collection: AsyncIOMotorCollection):
        self._db_collection = db_collection

    async def create(self, student: UpdateRoomModel) -> str:
        insert_result = await self._db_collection.insert_one(dict(student))
        return str(insert_result.inserted_id)

    async def create_many(self, rooms: List[UpdateRoomModel]) -> list[str]:
        rooms_dict = [dict(room) for room in rooms]

        insert_result = await self._db_collection.insert_many(rooms_dict)
        mapped_to_str_ids = list(map(str, insert_result.inserted_ids))
        return mapped_to_str_ids

    async def get_all(self) -> list[Room]:
        db_students = []
        async for student in self._db_collection.find():
            db_students.append(MongoDBManager.map_room(student))
        return db_students

    async def get_by_id(self, student_id: str) -> Room | None:
        print(f'Get student {student_id} from mongo')
        db_student = await self._db_collection.find_one(MongoDBManager.get_filter(student_id))
        return MongoDBManager.map_room(db_student)

    async def update(self, student_id: str, student: UpdateRoomModel) -> Room | None:
        db_student = await self._db_collection.find_one_and_replace(MongoDBManager.get_filter(student_id), dict(student))
        return MongoDBManager.map_room(db_student)

    async def delete(self, student_id: str) -> Room | None:
        db_student = await self._db_collection.find_one_and_delete(MongoDBManager.get_filter(student_id))
        return MongoDBManager.map_room(db_student)

    @staticmethod
    def get_instance(db_collection: AsyncIOMotorCollection = Depends(MongoDBManager.get_db_collection)):
        return Repository(db_collection)
