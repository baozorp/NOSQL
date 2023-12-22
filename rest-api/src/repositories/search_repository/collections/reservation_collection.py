from fastapi import Depends
import os
from elasticsearch import AsyncElasticsearch
from pydantic import BaseModel
from repositories.search_repository.elastic_search import ElasticSearch
from utils.elasticsearch_utils import ElsaticSearchManager


class ElasticReservationsCollection(ElasticSearch):
    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        super().__init__(index, elasticsearch_client)

    async def find_by_date(self, model: type[BaseModel], in_date: int, out_date: int):
        index_exist = await self._elasticsearch_client.indices.exists(index=self._elasticsearch_index)
        a = await self._elasticsearch_client.indices.get_alias()
        print(list(a.keys()))
        if not index_exist:
            return []

        query = {
            "bool": {
                "must_not": {
                    "bool": {
                        "filter": [
                            {"range": {"indate": {"lte": out_date}}},
                            {"range": {"outdate": {"gte": in_date}}}
                        ]
                    }
                }
            }
        }
        aggs = {
            "aggs": {
                "rooms_without_bookings": {
                    # Укажите размер в соответствии с вашими потребностями
                    "terms": {"field": "id_room", "size": 10}
                }
            }
        }
        result_list = []
        scroll = "1m"
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=query, scroll=scroll, aggs=aggs)
        if 'hits' not in response.body:
            return []
        value_of_matches = int(response['hits']['total']['value']/10) + 1
        scroll_id = response['_scroll_id']
        for _ in range(value_of_matches):
            hits = response.body['hits']['hits']
            for hit in hits:
                hit['_source']['id'] = hit['_id']
            priv_result = [
                model.model_validate(hit['_source']) for hit in hits]
            result_list += priv_result
            response = await self._elasticsearch_client.scroll(scroll='1m', scroll_id=scroll_id)
        return result_list

    @staticmethod
    def get_instance(elasticsearch_client: AsyncElasticsearch = Depends(ElsaticSearchManager.get_elasticsearch_client)):
        elasticsearch_index: str = str(os.getenv('RESERVATIONS_COLLECTION'))
        return ElasticReservationsCollection(elasticsearch_index, elasticsearch_client)
