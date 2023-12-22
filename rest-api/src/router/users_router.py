from typing import Any, List
from fastapi import APIRouter, Depends
from repositories.mongo.collections.users_collection import MongoUsersCollection
from repositories.search_repository.collections.users_collection import ElasticUsersCollection
from models.users import User
import asyncio


router = APIRouter()


@router.get("/")
async def get_all_hosts() -> list[str]:
    return ["Hello,", "world!"]


@router.post("/")
async def add_user(user: User,
                   repository: MongoUsersCollection = Depends(
                       MongoUsersCollection.get_instance),
                   search_repository: ElasticUsersCollection = Depends(ElasticUsersCollection.get_instance)) -> str:
    room_id = await repository.create(user)
    await search_repository.create(room_id, user)
    return 'room_id'
