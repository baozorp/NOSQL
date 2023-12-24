from typing import Any, Coroutine, Mapping, Sequence
from fastapi import Depends
import json
from pydantic import BaseModel
from models.room import Room, UpdateRoomModel
from models.users import User, UserUpdate
from models.reservation import UpdateReservation
from repositories.mongo.mongodb import MongoDBCollection
from repositories.mongo.collections.rooms_collection import MongoRoomCollection
from repositories.mongo.collections.users_collection import MongoUsersCollection
from repositories.mongo.collections.reservation_collection import MongoReservationCollection
from repositories.search_repository.collections.reservation_collection import ElasticReservationsCollection
from repositories.search_repository.elastic_search import ElasticSearch
import asyncio
from datetime import datetime, timedelta
import random


class DataLoader:

    @staticmethod
    async def load_data(file_name, mongodb: MongoDBCollection,  elasticdb: ElasticSearch):
        model: type[BaseModel]
        match file_name:
            case "rooms":
                model = UpdateRoomModel
            case "users":
                model = UserUpdate
            case _:
                raise ValueError("File is not exist")
        with open(f'data_loading/{file_name}.json', 'r') as rooms_json:
            objs = json.load(rooms_json)

        roomsModels: Sequence[BaseModel] = [
            model.model_validate(obj) for obj in objs]
        rooms_ids = await mongodb.create_many(roomsModels)
        asyncio.create_task(
            elasticdb.create_many(rooms_ids, objs))
        print("Info was added")

    @staticmethod
    async def generate_data(tasks: Sequence[Coroutine[Any, Any, str]],
                            room_repository: MongoRoomCollection,
                            user_repository: MongoUsersCollection,
                            reservations_mongo: MongoReservationCollection,
                            reservations_elastic: ElasticReservationsCollection
                            ):
        await asyncio.gather(*tasks)
        rooms = await room_repository.get_all(Room)
        users = await user_repository.get_all(User)
        print("Reservations generation started")
        room_list = [i.model_dump()['id']for i in rooms]
        user_list = [i.model_dump()['id']for i in users]
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2020, 12, 31)
        data: Sequence[Mapping[str, Any]] = []
        for i in range(len(room_list)):
            user_id = random.choice(user_list)
            room_id = room_list[i]
            in_date = (
                start_date + timedelta(days=random.randint(0, (end_date - start_date).days)))
            out_date = (
                in_date + timedelta(days=random.randint(1, 30))).strftime('%Y%m%d')
            in_date = in_date.strftime('%Y%m%d')
            is_paid = random.choice([True])

            entry = {
                'user_id': user_id,
                'room_id': room_id,
                'in_date': int(in_date),
                'out_date': int(out_date),
                'isPaid': is_paid
            }

            data.append(entry)
        objs: Sequence[BaseModel] = [
            UpdateReservation.model_validate(i) for i in data]
        reserv_id = await reservations_mongo.create_many(objs)

        print("Reservation information loaded into mongo")
        asyncio.create_task(reservations_elastic.create_many(reserv_id, data))
        # print("Info generated, but loading")
        # return data
