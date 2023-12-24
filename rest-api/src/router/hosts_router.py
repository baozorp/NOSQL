from typing import Any, Sequence
from bson import ObjectId
from fastapi import APIRouter, status, Depends
from pymemcache import HashClient
from starlette.responses import Response
from repositories.mongo.mongodb import MongoDBCollection
from utils.memcached_utils import MemcachedManager
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.search_repository.collections.rooms_collection import ElasticRoomsCollection
from repositories.search_repository.elastic_search import ElasticSearch
from models.room import Room, RoomUpdate

router = APIRouter()


@router.get("/")
async def get_all_hosts(repository: MongoRoomCollection = Depends(MongoRoomCollection.get_instance)) -> Sequence[Room]:
    result: Sequence[Room] = [Room.model_validate(user) for user in await repository.get_all(Room)]
    return result


@router.get("/filter_by_description")
async def filter_by_description(description: str, repository: ElasticSearch = Depends(ElasticRoomsCollection.get_instance)) -> Any:
    return await repository.find_by_atr(Room, "description", description)


@router.get("/filter_by_location")
async def filter_by_location(host_location: str, repository: ElasticSearch = Depends(ElasticRoomsCollection.get_instance)) -> Any:
    return await repository.find_by_atr(Room, "host_location", host_location)


@router.get("/clear_collection")
async def drop_collection_by_name(
        repository: MongoDBCollection = Depends(
            MongoRoomCollection.get_instance),
        search_repository: ElasticRoomsCollection = Depends(ElasticRoomsCollection.get_instance)) -> Any:
    await repository.clear_collection()
    await search_repository.clear_collection()
    return "Succesfully cleared"


@router.get("/find_by_id", response_model=Room)
async def get_by_id(id: str,
                    repository: MongoRoomCollection = Depends(
                        MongoRoomCollection.get_instance)) -> Any:
    if not ObjectId.is_valid(id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.get_by_id(RoomUpdate, id)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return obj


@router.put("/")
async def add_room(room: RoomUpdate,
                   repository: MongoDBCollection = Depends(
                       MongoRoomCollection.get_instance),
                   search_repository: ElasticSearch = Depends(ElasticRoomsCollection.get_instance)) -> str:
    room_id = await repository.create(room)
    await search_repository.create(room_id, RoomUpdate.model_dump(room))
    return room_id


@router.delete("/{obj_id}")
async def remove_obj(obj_id: str,
                     repository: MongoRoomCollection = Depends(
                         MongoRoomCollection.get_instance),
                     search_repository: ElasticSearch = Depends(ElasticRoomsCollection.get_instance)) -> Response:
    if not ObjectId.is_valid(obj_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.delete(obj_id, Room)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.delete(obj_id)
    return Response()


@router.put("/{obj_id}", response_model=Room)
async def update_obj(obj_id: str,
                     obj_update_model: RoomUpdate,
                     repository: MongoDBCollection = Depends(
                         MongoRoomCollection.get_instance),
                     search_repository: ElasticSearch = Depends(ElasticRoomsCollection.get_instance)) -> Any:
    if not ObjectId.is_valid(obj_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.update(obj_update_model, Room, obj_id)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.update(obj_id, obj_update_model)
    return obj
