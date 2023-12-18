from fastapi import APIRouter, Depends
import asyncio
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.search_repository.collections.rooms_collection import ElsaticRoomsCollection
from data_loading.load_data import DataLoader


router = APIRouter()


@router.get("/")
async def get_all_hostss() -> list[str]:
    return ["Hello,", "worldasdsa!"]


@router.get("/load")
async def load_data(
        repository: MongoRoomCollection = Depends(
            MongoRoomCollection.get_instance),
        search_repository: ElsaticRoomsCollection = Depends(ElsaticRoomsCollection.get_instance)) -> str:
    asyncio.create_task(DataLoader().load_rooms(
        mongodb=repository, elasticdb=search_repository))
    return "Hello, world!"
