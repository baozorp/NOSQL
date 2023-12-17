from pymemcache import HashClient
import os
from cache.json_serializer import JsonSerializer
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

memcached_client: HashClient


class MemcachedManager:

    @staticmethod
    def get_memcached_client() -> HashClient:
        global memcached_client
        return memcached_client

    @staticmethod
    def init_memcached_client():
        global memcached_client
        MEMCACHED_URL = str(os.getenv('MEMCACHED_URL'))
        memcached_servers: list = MEMCACHED_URL.split(',')
        json_ser = JsonSerializer()
        try:
            memcached_client = HashClient(memcached_servers, serde=json_ser)
            print(f'Connected to memcached with uri {MEMCACHED_URL}')
        except Exception as ex:
            print(f'Cant connect to memcached: {ex}')

    @staticmethod
    def close_memcached_connect():
        global memcached_client
        if memcached_client is None:
            return
        memcached_client.close()
