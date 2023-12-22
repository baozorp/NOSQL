from fastapi import Depends
import os
from elasticsearch import AsyncElasticsearch
from repositories.search_repository.elastic_search import ElsaticSearch
from utils.elasticsearch_utils import ElsaticSearchManager


class ElasticRoomsCollection(ElsaticSearch):
    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        super().__init__(index, elasticsearch_client)

    @staticmethod
    def get_instance(elasticsearch_client: AsyncElasticsearch = Depends(ElsaticSearchManager.get_elasticsearch_client)):
        elasticsearch_index: str = str(os.getenv('ROOMS_COLLECTION'))
        return ElasticRoomsCollection(elasticsearch_index, elasticsearch_client)

    async def find_by_description(self, description: str):
        index_exist = await self._elasticsearch_client.indices.exists(index=self._elasticsearch_index)
        if not index_exist:
            return []
        query = {
            "bool": {
                "must": [
                    {
                        "fuzzy": {
                            "description": {
                                "value": description
                            }
                        }
                    }
                ]
            }
        }
        result_list = []
        scroll = "1m"
        response = await self._elasticsearch_client.search(index=self._elasticsearch_index, query=query, scroll=scroll)
        if 'hits' not in response.body:
            return []
        value_of_matches = int(response['hits']['total']['value']/10) + 1
        scroll_id = response['_scroll_id']
        for _ in range(value_of_matches):
            hits = response.body['hits']['hits']
            priv_result = [{
                'id': hits[i]['_id'],
                'description': hits[i]['_source']['description'],
                'price': hits[i]['_source']['price'], } for i in range(len(hits))]
            result_list += priv_result
            response = await self._elasticsearch_client.scroll(scroll='1m', scroll_id=scroll_id)

        # rooms = list(map(lambda room:
        #                  Room(
        #                      id=room['_id'],
        #                      description=room['_source']['description']
        #                  ),
        #                  result))
        return result_list
