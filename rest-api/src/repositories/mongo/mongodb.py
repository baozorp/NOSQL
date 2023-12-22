from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import List, Sequence, Type

from pydantic import BaseModel

from utils.mongo_manager import MongoDBManager
from models.room import Room, UpdateRoomModel


class MongoDBCollection:

    _db: AsyncIOMotorDatabase
    _db_collection: AsyncIOMotorCollection

    def __init__(self, db: AsyncIOMotorDatabase, db_collection: AsyncIOMotorCollection):
        self._db: AsyncIOMotorDatabase = db
        self._db_collection: AsyncIOMotorCollection = db_collection

    async def clear_collection(self):
        collection_name: str = str(self._db_collection.name)
        try:
            await self._db.drop_collection(collection_name)
            await self._db.create_collection(collection_name)
        except Exception as e:
            print(f"Unsuccesfull drop: {e}")
            return "Unsuccess"
        return "Success"

    async def create(self, student) -> str:
        insert_result = await self._db_collection.insert_one(dict(student))
        return str(insert_result.inserted_id)

    async def create_many(self, rooms: Sequence[BaseModel]) -> list[str]:
        rooms_dict = [dict(room) for room in rooms]
        insert_result = await self._db_collection.insert_many(rooms_dict)
        mapped_to_str_ids = list(map(str, insert_result.inserted_ids))
        return mapped_to_str_ids

    async def get_all(self, baseModel: Type[BaseModel]) -> Sequence[BaseModel]:
        db_objs: Sequence = []
        async for student in self._db_collection.find():
            student['id'] = str(student['_id'])
            db_objs.append(baseModel.model_validate(student))
        return db_objs

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
