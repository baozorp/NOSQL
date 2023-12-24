from ast import mod
from sre_constants import ANY
from bson import ObjectId
from elasticsearch_dsl import Object
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import Any, Mapping, Sequence

from pydantic import BaseModel


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

    async def create(self, obj: BaseModel) -> str:
        insert_result = await self._db_collection.insert_one(obj.model_dump())
        return str(insert_result.inserted_id)

    async def create_many(self, objs: Sequence[BaseModel]) -> list[str]:
        objs_dict = [dict(obj) for obj in objs]
        insert_result = await self._db_collection.insert_many(objs_dict)
        mapped_to_str_ids = list(map(str, insert_result.inserted_ids))
        return mapped_to_str_ids

    async def excepting_searh(self, baseModel: type[BaseModel], ids: Sequence[ObjectId]) -> Sequence[BaseModel]:
        db_objs: Sequence[baseModel] = []
        async for obj in self._db_collection.find({"_id": {"$nin": ids}}):
            obj['id'] = str(obj['_id'])
            db_objs.append(baseModel.model_validate(obj))
        return db_objs

    async def get_all(self, baseModel: type[BaseModel]) -> Sequence[BaseModel]:
        db_objs: Sequence[BaseModel] = []
        async for obj in self._db_collection.find():
            obj['id'] = str(obj['_id'])
            db_objs.append(baseModel.model_validate(obj))
        return db_objs

    async def get_by_id(self, model: type[BaseModel], obj_id: str) -> BaseModel | None:
        db_obj: Mapping[str, Any] | None = await self._db_collection.find_one({'_id': ObjectId(obj_id)})
        if db_obj:
            validate_object = model.model_validate(db_obj)
            return validate_object
        return None

    async def update(self, updateModel: BaseModel, model: type[BaseModel], obj_id: str) -> BaseModel | None:
        db_obj: Mapping[str, Any] = await self._db_collection.find_one_and_replace({'_id': ObjectId(obj_id)}, updateModel.model_dump())
        if db_obj:
            validate_object = model.model_validate(db_obj)
            return validate_object
        return None

    async def delete(self, obj_id: str, model: type[BaseModel]) -> BaseModel | None:
        db_obj = await self._db_collection.find_one_and_delete({'_id': ObjectId(obj_id)})
        if db_obj:
            validate_object = model.model_validate(db_obj)
            return validate_object
        return None
