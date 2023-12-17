import os
from typing import Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from models.room import Room
from motor.core import AgnosticCollection
import pymongo
db_client: AsyncIOMotorClient


class MongoDBManager:

    @staticmethod
    async def get_db_collection() -> AsyncIOMotorCollection:
        mongo_db_name: str = str(os.getenv('MONGO_DB'))
        collection_name: str = str(os.getenv('MONGO_COLLECTION'))
        mongo_collection = AsyncIOMotorCollection(
            db_client.get_database(mongo_db_name), name=collection_name)
        return mongo_collection

    @staticmethod
    async def init_mongo_client(mongo_url: str = str(os.getenv('MONGO_URL')),
                                mongo_db: str = str(os.getenv('MONGO_DB')),
                                mongo_collection: str = str(os.getenv(
                                    'MONGO_COLLECTION'))
                                ):
        global db_client
        try:
            print(os.getenv('MONGO_URL'))
            db_client = AsyncIOMotorClient(mongo_url)
            await db_client.server_info()
            print(f'Connected to mongo with uri {mongo_url}')
            if mongo_db not in await db_client.list_database_names():
                data_base = await db_client.get_database(mongo_db)
                await db_client.get_database(
                    mongo_db).create_collection(mongo_collection)
                print(f'Database {mongo_db} created')

        except Exception as ex:
            print(f'Cant connect to mongo: {ex}')

    @staticmethod
    def close_connection():
        global db_client
        db_client.close() if db_client else None

    @staticmethod
    def get_filter(id: str) -> dict:
        return {'_id': ObjectId(id)}

    @staticmethod
    def map_room(room_data: Any) -> Room | None:
        if room_data is None:
            return None

        return Room(
            id=str(room_data['_id']),
            host_location=room_data['host_location'],
            room_type=room_data['room_type'],
            description=room_data['description'],
            bedrooms=room_data['bedrooms'],
            accommodates=room_data['accommodates'],
            price=room_data['price']
        )
