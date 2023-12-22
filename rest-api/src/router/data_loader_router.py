from typing import Any, Coroutine, Sequence
from fastapi import APIRouter, Depends
import asyncio
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.mongo.collections.users_collection import MongoUsersCollection
from repositories.mongo.collections.reservation_collection import MongoReservationCollection
from repositories.search_repository.collections.rooms_collection import ElasticRoomsCollection
from repositories.search_repository.collections.users_collection import ElasticUsersCollection
from repositories.search_repository.collections.reservation_collection import ElasticReservationsCollection
from repositories.mongo.mongodb import MongoDBCollection
from repositories.search_repository.elastic_search import ElasticSearch
from data_loading.load_data import DataLoader
import os

router = APIRouter()


@router.get("/")
async def get_all_hostss() -> list[str]:
    return ["Hello,", "worldasdsa!"]


@router.get("/load_all")
async def load_data(
    room_repository: MongoRoomCollection = Depends(
        MongoRoomCollection.get_instance),
    user_repository: MongoUsersCollection = Depends(
        MongoUsersCollection.get_instance),
    reservations_mongo: MongoReservationCollection = Depends(
        MongoReservationCollection.get_instance),
    rooms_search_repository: ElasticRoomsCollection = Depends(
        ElasticRoomsCollection.get_instance),
    users_search_repository: ElasticSearch = Depends(
        ElasticUsersCollection.get_instance),
    reservations_elastic: ElasticReservationsCollection = Depends(
        ElasticReservationsCollection.get_instance),

) -> str:
    tasks: Sequence[Coroutine[Any, Any, str]] = [
        load_rooms(room_repository, rooms_search_repository),
        load_users(user_repository, users_search_repository)
    ]
    asyncio.create_task(DataLoader.generate_data(tasks,
                                                 room_repository,
                                                 user_repository,
                                                 reservations_mongo,
                                                 reservations_elastic
                                                 ))
    return "Hello, world!"


@router.get("/load_rooms")
async def load_rooms(
        rooms_repository: MongoDBCollection = Depends(
            MongoRoomCollection.get_instance),
        rooms_search_repository: ElasticRoomsCollection = Depends(
            ElasticRoomsCollection.get_instance),
) -> str:
    file_name = os.getenv('ROOMS_COLLECTION')
    task = DataLoader.load_data(file_name=file_name,
                                mongodb=rooms_repository,
                                elasticdb=rooms_search_repository)
    await asyncio.create_task(task)
    return "Rooms was loaded"


@router.get("/load_users")
async def load_users(
        users_repository: MongoDBCollection = Depends(
            MongoUsersCollection.get_instance),
        users_search_repository: ElasticSearch = Depends(
            ElasticUsersCollection.get_instance),
) -> str:
    file_name = os.getenv('USERS_COLLECTION')
    task = DataLoader.load_data(file_name=file_name,
                                mongodb=users_repository,
                                elasticdb=users_search_repository)
    await asyncio.create_task(task)
    return "Users was loaded"
