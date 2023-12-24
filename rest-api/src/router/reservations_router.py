from typing import Any, Sequence, Set
from bson import ObjectId
from fastapi import APIRouter, Depends
from repositories.mongo.collections.reservation_collection import MongoReservationCollection, MongoDBCollection
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.search_repository.collections.reservation_collection import ElasticReservationsCollection, ElasticSearch
from models.reservation import Reservation, UpdateReservation
from models.room import Room

router = APIRouter()


@router.get("/")
async def get_all_hosts(repository: MongoReservationCollection = Depends(MongoReservationCollection.get_instance)) -> Sequence[Reservation]:
    result: Sequence[Reservation] = [Reservation.model_validate(user) for user in await repository.get_all(Reservation)]
    return result


@router.get("/find_by_date")
async def find_by_date(
        current_date: int,
        in_date: int,
        out_date: int,
        repository: MongoDBCollection = Depends(
            MongoRoomCollection.get_instance),
        search_repository: ElasticReservationsCollection = Depends(ElasticReservationsCollection.get_instance)):
    bad_results: Sequence[ObjectId] = await search_repository.find_by_date(current_date, in_date, out_date)
    good_results = await repository.excepting_searh(Room, bad_results)
    return good_results


@router.get("/clear_collection")
async def clear_collection(
        repository: MongoDBCollection = Depends(
            MongoReservationCollection.get_instance),
        search_repository: ElasticSearch = Depends(ElasticReservationsCollection.get_instance)) -> Any:
    await repository.clear_collection()
    await search_repository.clear_collection()
    return "Succesfully cleared"


@router.put("/add_reservation")
async def add_reservation(
        reservation: UpdateReservation,
        repository: MongoDBCollection = Depends(
            MongoReservationCollection.get_instance),
        search_repository: ElasticSearch = Depends(ElasticReservationsCollection.get_instance)):
    reservation_id = await repository.create(reservation)
    await search_repository.create(reservation_id, UpdateReservation.model_dump(reservation))
    print(reservation_id)
    return reservation_id
