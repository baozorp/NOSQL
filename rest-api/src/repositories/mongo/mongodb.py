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

    async def create(self, obj) -> str:
        insert_result = await self._db_collection.insert_one(dict(obj))
        return str(insert_result.inserted_id)

    async def create_many(self, objs: Sequence[BaseModel]) -> list[str]:
        rooms_dict = [dict(obj) for obj in objs]
        insert_result = await self._db_collection.insert_many(rooms_dict)
        mapped_to_str_ids = list(map(str, insert_result.inserted_ids))
        return mapped_to_str_ids

    async def get_all(self, baseModel: Type[BaseModel]) -> Sequence[BaseModel]:
        db_objs: Sequence = []
        async for obj in self._db_collection.find():
            obj['id'] = str(obj['_id'])
            db_objs.append(baseModel.model_validate(obj))
        return db_objs

    async def get_by_id(self, obj_id: str) -> Room | None:
        print(f'Get obj {obj_id} from mongo')
        db_objs = await self._db_collection.find_one(MongoDBManager.get_filter(obj_id))
        return MongoDBManager.map_room(db_objs)

    async def update(self, obj_id: str, obj: UpdateRoomModel) -> Room | None:
        db_objs = await self._db_collection.find_one_and_replace(MongoDBManager.get_filter(obj_id), dict(obj))
        return MongoDBManager.map_room(db_objs)

    async def delete(self, obj_id: str) -> Room | None:
        db_objs = await self._db_collection.find_one_and_delete(MongoDBManager.get_filter(obj_id))
        return MongoDBManager.map_room(db_objs)
