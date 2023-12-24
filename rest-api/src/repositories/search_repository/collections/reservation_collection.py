from typing import Sequence, Set
from fastapi import Depends
import os
from elasticsearch import AsyncElasticsearch
from bson import ObjectId
from repositories.search_repository.elastic_search import ElasticSearch
from utils.elasticsearch_utils import ElsaticSearchManager


class ElasticReservationsCollection(ElasticSearch):
    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        super().__init__(index, elasticsearch_client)

    async def find_by_date(self, current_date: int,  in_date: int, out_date: int) -> Sequence[ObjectId]:
        index_exist = await self._elasticsearch_client.indices.exists(index=self._elasticsearch_index)
        if not index_exist:
            return []

        query = {
            "bool": {
                "must": [
                    {
                        "range": {
                            "in_date": {
                                "gte": current_date
                            }
                        }
                    }
                ],
                "should": [
                    {
                        "bool": {
                            "must": [
                                {"range": {"in_date": {"lte": in_date}}},
                                {"range": {"out_date": {"gte": in_date}}}
                            ]
                        }
                    },
                    {
                        "bool": {
                            "must": [
                                {"range": {"in_date": {"gte": in_date}}},
                                {"range": {"out_date": {"lte": out_date}}}
                            ]
                        }
                    },
                    {
                        "bool": {
                            "must": [
                                {"range": {"in_date": {"lte": out_date}}},
                                {"range": {"out_date": {"gte": out_date}}}
                            ]
                        }
                    }
                ]
            }
        }

        properties = {
            "room_id": {
                "type": "text",
                "fielddata": True
            }
        }
        scroll = '1m'
        await self._elasticsearch_client.indices.put_mapping(index=self._elasticsearch_index, properties=properties)
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=query, scroll=scroll)
        result_set: Set[ObjectId] = set()
        scroll_id = response['_scroll_id']
        value = response['hits']['total']['value']
        print(value)
        chunks = int(value/10) + 1

        for _ in range(chunks):
            hits = response['hits']['hits']
            for hit in hits:
                result_set.add(ObjectId(hit['_source']['room_id']))
            response = await self._elasticsearch_client.scroll(scroll_id=scroll_id, scroll=scroll)
        result_list: Sequence[ObjectId] = list(result_set)
        return result_list

    @staticmethod
    def get_instance(elasticsearch_client: AsyncElasticsearch = Depends(ElsaticSearchManager.get_elasticsearch_client)):
        elasticsearch_index: str = str(os.getenv('RESERVATIONS_COLLECTION'))
        return ElasticReservationsCollection(elasticsearch_index, elasticsearch_client)
