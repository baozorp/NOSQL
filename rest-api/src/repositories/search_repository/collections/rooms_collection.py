from fastapi import Depends
import os
from elasticsearch import AsyncElasticsearch
from repositories.search_repository.elastic_search import ElsaticSearch
from utils.elasticsearch_utils import ElsaticSearchManager


class ElsaticRoomsCollection(ElsaticSearch):
    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        super().__init__(index, elasticsearch_client)

    @staticmethod
    def get_instance(elasticsearch_client: AsyncElasticsearch = Depends(ElsaticSearchManager.get_elasticsearch_client)):
        elasticsearch_index: str = str(os.getenv('ROOMS_COLLECTIONS'))
        return ElsaticRoomsCollection(elasticsearch_index, elasticsearch_client)
