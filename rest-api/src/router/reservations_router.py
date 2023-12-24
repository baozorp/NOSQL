from typing import Any, Mapping, Sequence
from bson import ObjectId
from fastapi import APIRouter, Depends, status, Response
from repositories.mongo.collections.reservation_collection import MongoReservationCollection, MongoDBCollection
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.search_repository.collections.reservation_collection import ElasticReservationsCollection, ElasticSearch
from models.reservation import Reservation, ReservationUpdate
from models.room import Room
from pymemcache import HashClient
from utils.memcached_utils import MemcachedManager
from datetime import datetime, timedelta

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
        reservation: ReservationUpdate,
        repository: MongoDBCollection = Depends(
            MongoReservationCollection.get_instance),
        hashClient: HashClient = Depends(MemcachedManager.get_memcached_client)):

    memcached_value = hashClient.get(reservation.room_id)

    result_dict: Mapping[str, Any] = {}
    reservation_has_intersection = False
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    answer: str = ""
    if memcached_value and isinstance(memcached_value, Mapping):
        for reservation_time in memcached_value:
            saved_time = datetime.strptime(
                reservation_time, "%Y-%m-%d %H:%M:%S")
            time_difference = current_time - saved_time
            if time_difference >= timedelta(minutes=15):
                continue
            result_dict[reservation_time] = memcached_value[reservation_time]
            memcached_in_date = memcached_value[reservation_time]['in_date']
            memcached_out_date = memcached_value[reservation_time]['out_date']
            condition1 = memcached_in_date <= reservation.in_date and memcached_out_date >= reservation.in_date
            condition2 = memcached_in_date >= reservation.in_date and memcached_out_date <= reservation.out_date
            condition3 = memcached_in_date <= reservation.out_date and memcached_out_date >= reservation.in_date

            if condition1 or condition2 or condition3:
                reservation_has_intersection = True

        if not reservation_has_intersection:
            result_dict[formatted_time] = reservation.model_dump()
        hashClient.replace(reservation.room_id, result_dict, expire=60*15)

    else:
        result_dict[formatted_time] = reservation.model_dump()
        hashClient.add(reservation.room_id, result_dict, expire=60*15)
    answer: str = await repository.create(reservation) if not reservation_has_intersection else "Reservation has intersection with others"
    return answer


@router.put("/delete_reservation")
async def update_reservation(reservation: Reservation,
                             repository: MongoDBCollection = Depends(
                                 MongoReservationCollection.get_instance),
                             hashClient: HashClient = Depends(
                                 MemcachedManager.get_memcached_client),
                             search_repository: ElasticReservationsCollection = Depends(ElasticReservationsCollection.get_instance)):
    memcached_value = hashClient.get(reservation.room_id)
    # TODO проверка по истечению времени бронирования
    if memcached_value and isinstance(memcached_value, dict):
        if reservation.room_id in memcached_value:
            memcached_value[reservation.room_id]
    reservation.isPaid = True
    await repository.update(reservation, ReservationUpdate, reservation.id)
    await search_repository.update(reservation.id, reservation)


@router.put("/{obj_id}", response_model=Room)
async def update_obj(obj_id: str,
                     obj_update_model: ReservationUpdate,
                     repository: MongoDBCollection = Depends(
                         MongoReservationCollection.get_instance),
                     search_repository: ElasticSearch = Depends(ElasticReservationsCollection.get_instance)) -> Any:
    if not ObjectId.is_valid(obj_id):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    obj = await repository.update(obj_update_model, Reservation, obj_id)
    if obj is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await search_repository.update(obj_id, obj_update_model)
    return obj
