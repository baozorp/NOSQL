from typing import Any, List, Sequence
import json
from multiprocessing.managers import BaseManager
from pydantic import BaseModel
from models.room import UpdateRoomModel
from models.users import UserUpdate
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.search_repository.collections.rooms_collection import ElasticRoomsCollection
from repositories.mongo.collections.users_collection import MongoUsersCollection
from repositories.search_repository.collections.users_collection import ElasticUsersCollection
from repositories.mongo.mongodb import MongoDBCollection
from repositories.search_repository.elastic_search import ElsaticSearch
import asyncio


class DataLoader:

    @staticmethod
    async def load_data(file_name, mongodb: MongoDBCollection,  elasticdb: ElsaticSearch):
        model: type[BaseModel]
        match file_name:
            case "rooms":
                model = UpdateRoomModel
            case "users":
                model = UserUpdate
            case _:
                raise ValueError("File is not exist")
        with open(f'data_loading/{file_name}.json', 'r') as rooms_json:
            rooms = json.load(rooms_json)
        roomsModels: Sequence[BaseModel] = [
            model.model_validate(obj) for obj in rooms]
        rooms_ids = await mongodb.create_many(roomsModels)
        asyncio.create_task(elasticdb.create_many(rooms_ids, rooms))
        print("Info was added")
