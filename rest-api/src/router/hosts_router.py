from ast import Await
from typing import Any, List

from bson import ObjectId
from fastapi import APIRouter, status, Depends
from pymemcache import HashClient
from starlette.responses import Response
import asyncio
from utils.memcached_utils import MemcachedManager
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.search_repository.collections.rooms_collection import ElsaticRoomsCollection
from models.room import Room, UpdateRoomModel

router = APIRouter()


@router.get("/")
async def get_all_hosts(repository: MongoRoomCollection = Depends(MongoRoomCollection.get_instance)) -> list[Room]:
    return await repository.get_all()


@router.get("/filter")
async def get_by_name(name: str, repository: ElsaticRoomsCollection = Depends(ElsaticRoomsCollection.get_instance)) -> Any:
    return await repository.find_by_name(name)


@router.get("/clear_collection")
async def drop_collection_by_name(
        collection_name: str,
        repository: MongoRoomCollection = Depends(
            MongoRoomCollection.get_instance),
        search_repository: ElsaticRoomsCollection = Depends(ElsaticRoomsCollection.get_instance)) -> Any:
    print(collection_name)
    a = await repository.drop_collection()
    b = await search_repository.clear_collection(name_of_index=collection_name)
    return "Succesfully cleared"


@router.get("/by_id?id={student_id}", response_model=Room)
async def get_by_id(student_id: str,
                    repository: MongoRoomCollection = Depends(
                        MongoRoomCollection.get_instance),
                    memcached_client: HashClient = Depends(MemcachedManager.get_memcached_client)) -> Any:
    if not ObjectId.is_valid(student_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    student = memcached_client.get(student_id)

    if student is not None:
        return student
    student = await repository.get_by_id(student_id)
    if student is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    memcached_client.add(student_id, student)

    return student


@router.post("/")
async def add_room(room: UpdateRoomModel,
                   repository: MongoRoomCollection = Depends(
                       MongoRoomCollection.get_instance),
                   search_repository: ElsaticRoomsCollection = Depends(ElsaticRoomsCollection.get_instance)) -> str:
    room_id = await repository.create(room)
    await search_repository.create(room_id, room)
    return room_id


@router.post("/set_many")
async def add_many_rooms(rooms: List[UpdateRoomModel],
                         repository: MongoRoomCollection = Depends(
                             MongoRoomCollection.get_instance),
                         search_repository: ElsaticRoomsCollection = Depends(ElsaticRoomsCollection.get_instance)) -> str:

    rooms_ids = await repository.create_many(rooms)
    elastic_tasks = [search_repository.create(
        rooms_ids[i], rooms[i]) for i in range(len(rooms_ids))]
    await asyncio.gather(*elastic_tasks)
    return 'student_id'


@router.delete("/{student_id}")
async def remove_student(student_id: str,
                         repository: MongoRoomCollection = Depends(
                             MongoRoomCollection.get_instance),
                         search_repository: ElsaticRoomsCollection = Depends(ElsaticRoomsCollection.get_instance)) -> Response:
    if not ObjectId.is_valid(student_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    student = await repository.delete(student_id)
    if student is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.delete(student_id)
    return Response()


@router.put("/{student_id}", response_model=Room)
async def update_student(student_id: str,
                         student_model: UpdateRoomModel,
                         repository: MongoRoomCollection = Depends(
                             MongoRoomCollection.get_instance),
                         search_repository: ElsaticRoomsCollection = Depends(ElsaticRoomsCollection.get_instance)) -> Any:
    if not ObjectId.is_valid(student_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    student = await repository.update(student_id, student_model)
    if student is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.update(student_id, student_model)
    return student
