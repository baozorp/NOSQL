from typing import Any, Sequence
from bson import ObjectId
from fastapi import APIRouter, Depends, status, Response
from repositories.search_repository.elastic_search import ElasticSearch
from fastapi import APIRouter, Depends
from repositories.mongo.collections.users_collection import MongoUsersCollection
from repositories.mongo.mongodb import MongoDBCollection
from repositories.search_repository.collections.users_collection import ElasticUsersCollection
from models.users import User, UserUpdate


router = APIRouter()


@router.get("/")
async def get_all_users(repository: MongoDBCollection = Depends(MongoUsersCollection.get_instance)) -> Sequence[User]:
    result: Sequence[User] = [User.model_validate(user) for user in await repository.get_all(User)]
    return result


@router.get("/clear_collection")
async def drop_collection_by_name(
        repository: MongoUsersCollection = Depends(
            MongoUsersCollection.get_instance),
        search_repository: ElasticSearch = Depends(ElasticUsersCollection.get_instance)) -> str:
    await repository.clear_collection()
    await search_repository.clear_collection()
    return "Users collection is empty"


@router.put("/")
async def add_user(room: UserUpdate,
                   repository: MongoDBCollection = Depends(
                       MongoUsersCollection.get_instance),
                   search_repository: ElasticSearch = Depends(ElasticUsersCollection.get_instance)) -> str:
    room_id = await repository.create(room)
    await search_repository.create(room_id, UserUpdate.model_dump(room))
    return room_id


@router.delete("/{obj_id}")
async def remove_obj(obj_id: str,
                     repository: MongoDBCollection = Depends(
                         MongoUsersCollection.get_instance),
                     search_repository: ElasticSearch = Depends(ElasticUsersCollection.get_instance)) -> Response:
    if not ObjectId.is_valid(obj_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.delete(obj_id, User)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.delete(obj_id)
    return Response()


@router.put("/{obj_id}", response_model=User)
async def update_obj(obj_id: str,
                     obj_update_model: UserUpdate,
                     repository: MongoDBCollection = Depends(
                         MongoUsersCollection.get_instance),
                     search_repository: ElasticSearch = Depends(ElasticUsersCollection.get_instance)) -> Any:
    if not ObjectId.is_valid(obj_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.update(obj_update_model, User, obj_id)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.update(obj_id, obj_update_model)
    return obj
