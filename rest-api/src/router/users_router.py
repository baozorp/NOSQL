from typing import Any, List, Sequence

from pydantic import BaseModel
from repositories.search_repository.elastic_search import ElsaticSearch
from fastapi import APIRouter, Depends
from repositories.mongo.collections.users_collection import MongoUsersCollection
from repositories.mongo.mongodb import MongoDBCollection
from repositories.search_repository.collections.users_collection import ElasticUsersCollection
from models.users import User


router = APIRouter()


@router.get("/")
async def get_all_users(repository: MongoDBCollection = Depends(MongoUsersCollection.get_instance)) -> Sequence[User]:
    result: Sequence[User] = [User.model_validate(user) for user in await repository.get_all(User)]
    return result


@router.get("/clear_collection")
async def drop_collection_by_name(
        collection_name: str,
        repository: MongoDBCollection = Depends(
            MongoUsersCollection.get_instance),
        search_repository: ElsaticSearch = Depends(ElasticUsersCollection.get_instance)) -> Any:
    await repository.clear_collection()
    await search_repository.clear_collection(name_of_index=collection_name)


@router.post("/")
async def add_user(user: User,
                   repository: MongoUsersCollection = Depends(
                       MongoUsersCollection.get_instance),
                   search_repository: ElasticUsersCollection = Depends(ElasticUsersCollection.get_instance)) -> str:
    room_id = await repository.create(user)
    await search_repository.create(room_id, user)
    return 'room_id'
