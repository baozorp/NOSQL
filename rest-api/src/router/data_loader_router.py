from fastapi import APIRouter, Depends
import asyncio
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.mongo.collections.users_collection import MongoUsersCollection
from repositories.search_repository.collections.rooms_collection import ElasticRoomsCollection
from repositories.search_repository.collections.users_collection import ElasticUsersCollection
from repositories.mongo.mongodb import MongoDBCollection
from repositories.search_repository.elastic_search import ElsaticSearch
from data_loading.load_data import DataLoader
import os

router = APIRouter()


@router.get("/")
async def get_all_hostss() -> list[str]:
    return ["Hello,", "worldasdsa!"]


@router.get("/load_all")
async def load_data() -> str:
    tasks = [
        load_rooms(),
        load_users()
    ]
    asyncio.gather(*tasks)
    return "Hello, world!"


@router.get("/load_rooms")
async def load_rooms(
        rooms_repository: MongoUsersCollection = Depends(
            MongoRoomCollection.get_instance),
        rooms_search_repository: ElasticRoomsCollection = Depends(
            ElasticRoomsCollection.get_instance),
) -> str:
    file_name = os.getenv('ROOMS_COLLECTION')
    task = DataLoader.load_data(file_name=file_name,
                                mongodb=rooms_repository,
                                elasticdb=rooms_search_repository)
    asyncio.create_task(task)
    return "Rooms was loaded"


@router.get("/load_users")
async def load_users(
        rooms_repository: MongoDBCollection = Depends(
            MongoUsersCollection.get_instance),
        rooms_search_repository: ElsaticSearch = Depends(
            ElasticUsersCollection.get_instance),
) -> str:
    file_name = os.getenv('USERS_COLLECTION')
    task = DataLoader.load_data(file_name=file_name,
                                mongodb=rooms_repository,
                                elasticdb=rooms_search_repository)
    asyncio.create_task(task)
    return "Users was loaded"
