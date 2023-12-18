import json
import requests
from repositories.repository.collections.rooms_collection import MongoRoomCollection
from repositories.search_repository.collections.rooms_collection import ElsaticRoomsCollection
import asyncio


class DataLoader:

    async def load_rooms(self, mongodb: MongoRoomCollection,  elasticdb: ElsaticRoomsCollection):
        with open('data_loading/rooms.json') as rooms_json:
            rooms = json.load(rooms_json)
            # Разбиение списка на подсписки по 1000 элементов
        # rooms = [rooms[i:i+step] for i in range(0, len(rooms), step)]
        rooms_ids = await mongodb.create_many(rooms)
        elastic_tasks = [elasticdb.create(
            rooms_ids[i], rooms[i]) for i in range(len(rooms_ids))]
        asyncio.gather(*elastic_tasks)
        print("Info was added")

    async def load_names(self, mongodb: MongoRoomCollection,  elasticdb: ElsaticRoomsCollection):
        with open('data_loading/names.json') as rooms_json:
            rooms = json.load(rooms_json)
            # Разбиение списка на подсписки по 1000 элементов
        # rooms = [rooms[i:i+step] for i in range(0, len(rooms), step)]
        rooms_ids = await mongodb.create_many(rooms)
        elastic_tasks = [elasticdb.create(
            rooms_ids[i], rooms[i]) for i in range(len(rooms_ids))]
        asyncio.gather(*elastic_tasks)
        print("Info was added")
