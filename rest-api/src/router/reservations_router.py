from typing import Any, Sequence
from fastapi import APIRouter, Depends
from repositories.mongo.collections.reservation_collection import MongoReservationCollection, MongoDBCollection
from repositories.search_repository.collections.reservation_collection import ElasticReservationsCollection, ElasticSearch
from models.reservation import Reservation

router = APIRouter()


@router.get("/")
async def get_all_hosts(repository: MongoReservationCollection = Depends(MongoReservationCollection.get_instance)) -> Sequence[Reservation]:
    result: Sequence[Reservation] = [Reservation.model_validate(user) for user in await repository.get_all(Reservation)]
    return result


@router.get("/find_by_date")
async def find_by_date(in_date: int,
                       out_date: int,
                       repository: ElasticReservationsCollection = Depends(ElasticReservationsCollection.get_instance)) -> Sequence[Reservation]:
    return await repository.find_by_date(Reservation, in_date, out_date)


@router.get("/clear_collection")
async def clear_collection(
        repository: MongoDBCollection = Depends(
            MongoReservationCollection.get_instance),
        search_repository: ElasticSearch = Depends(MongoReservationCollection.get_instance)) -> Any:
    await repository.clear_collection()
    await search_repository.clear_collection()
    return "Succesfully cleared"
