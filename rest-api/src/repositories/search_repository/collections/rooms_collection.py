from fastapi import Depends
import os
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel
from repositories.search_repository.elastic_search import ElasticSearch
from utils.elasticsearch_utils import ElsaticSearchManager
from models.room import Room


class ElasticRoomsCollection(ElasticSearch):
    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        super().__init__(index, elasticsearch_client)

    @staticmethod
    def get_instance(elasticsearch_client: AsyncElasticsearch = Depends(ElsaticSearchManager.get_elasticsearch_client)):
        elasticsearch_index: str = str(os.getenv('ROOMS_COLLECTION'))
        return ElasticRoomsCollection(elasticsearch_index, elasticsearch_client)
