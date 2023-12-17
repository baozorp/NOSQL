from typing import Any, List

from bson import ObjectId
from fastapi import APIRouter, status, Depends
from pymemcache import HashClient
from starlette.responses import Response
import asyncio
from utils.memcached_utils import MemcachedManager
from repository.repository import Repository
from repository.search_repository import SearchStudentRepository
from models.room import Room, UpdateRoomModel

router = APIRouter()


@router.get("/")
async def get_all_hosts(repository: Repository = Depends(Repository.get_instance)) -> list[Room]:
    return await repository.get_all()


@router.get("/filter")
async def get_by_name(name: str, repository: SearchStudentRepository = Depends(SearchStudentRepository.get_instance)) -> Any:
    return await repository.find_by_name(name)


@router.get("/by_id/{student_id}", response_model=Room)
async def get_by_id(student_id: str,
                    repository: Repository = Depends(Repository.get_instance),
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
                   repository: Repository = Depends(
                       Repository.get_instance),
                   search_repository: SearchStudentRepository = Depends(SearchStudentRepository.get_instance)) -> str:
    room_id = await repository.create(room)
    await search_repository.create(room_id, room)
    return room_id


@router.post("/set_many")
async def add_many_students(rooms: List[UpdateRoomModel],
                            repository: Repository = Depends(
        Repository.get_instance),
        search_repository: SearchStudentRepository = Depends(SearchStudentRepository.get_instance)) -> str:
    rooms_ids = await repository.create_many(rooms)
    elastic_tasks = [search_repository.create(
        rooms_ids[i], rooms[i]) for i in range(len(rooms_ids))]
    await asyncio.gather(*elastic_tasks)
    return 'student_id'


@router.delete("/{student_id}")
async def remove_student(student_id: str,
                         repository: Repository = Depends(
                             Repository.get_instance),
                         search_repository: SearchStudentRepository = Depends(SearchStudentRepository.get_instance)) -> Response:
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
                         repository: Repository = Depends(
                             Repository.get_instance),
                         search_repository: SearchStudentRepository = Depends(SearchStudentRepository.get_instance)) -> Any:
    if not ObjectId.is_valid(student_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    student = await repository.update(student_id, student_model)
    if student is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.update(student_id, student_model)
    return student
