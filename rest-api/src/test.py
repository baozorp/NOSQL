import requests
import json


def set_rooms():
    with open('hosts.json') as rooms_json:
        rooms = json.load(rooms_json)

    # Разбиение списка на подсписки по 1000 элементов
    step = 2000

    rooms = [rooms[i:i+step] for i in range(0, len(rooms), step)]
    # print(rooms[0][0])
    for i in rooms:
        requests.post(
            'http://localhost:8005/api/rooms/set_many', json=i)


def get_by_description():
    string = 'sea'
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/filter?name={string}').json()


def get_by_id():
    id = '657f29abe26d9569cb709e37'
    return requests.get(
        f'http://127.0.0.1:8005/api/rooms/by_id/{id}').json()


def get_all():
    return requests.get(
        'http://127.0.0.1:8005/api/rooms/').json()


def clear_all():
    return requests.get(
        f"http://127.0.0.1:8005/api/rooms/clear_collection?collection_name=rooms").json()


set_rooms()
