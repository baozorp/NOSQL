import os
from typing import Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from models.room import Room

db_client: AsyncIOMotorClient


class MongoDBManager:

    @staticmethod
    async def init_mongo_client(mongo_url: str = str(os.getenv('MONGO_URL')),
                                mongo_db: str = str(os.getenv('MONGO_DB'))):
        global db_client
        try:
            db_client = AsyncIOMotorClient(mongo_url)
            await db_client.server_info()
            print(f'Connected to mongo with uri {mongo_url}')
            if mongo_db not in await db_client.list_database_names():
                db_client.get_database(mongo_db)
                print(f'Database {mongo_db} created')
        except Exception as ex:
            print(f'Cant connect to mongo: {ex}')

    @staticmethod
    async def get_db() -> AsyncIOMotorDatabase:
        global db_client
        mongo_db_name: str = str(os.getenv('MONGO_DB'))
        return AsyncIOMotorDatabase(db_client, name=mongo_db_name)

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
            price=room_data['price'],
            picture_url=room_data['picture_url']
        )
