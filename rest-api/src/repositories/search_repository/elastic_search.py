from typing import Any, Mapping, Sequence
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel


class ElasticSearch:
    _elasticsearch_client: AsyncElasticsearch
    _elasticsearch_index: str

    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        self._elasticsearch_client = elasticsearch_client
        self._elasticsearch_index = index

    async def clear_collection(self):
        try:
            await self._elasticsearch_client.indices.delete(index=self._elasticsearch_index)
            await self._elasticsearch_client.indices.create(index=self._elasticsearch_index)
        except Exception as e:
            print(f"Unsuccesfull clear: {e}")
            return "Unsuccess"
        else:
            return "Success"

    async def create(self, obj_id: str, obj: Mapping[str, Any]):
        await self._elasticsearch_client.create(index=self._elasticsearch_index, id=obj_id, document=obj)

    async def create_many(self, objects_ids: list[str], objects: Sequence[Mapping[str, Any]]):
        bulk = []
        for i in range(len(objects)):
            index_operation = {
                'index': {'_index': self._elasticsearch_index, '_id': objects_ids[i]}}
            bulk.append(index_operation)
            bulk.append(objects[i])

        chunk_size = 1000
        chunks = [bulk[i:i + chunk_size]
                  for i in range(0, len(bulk), chunk_size)]
        for i in range(len(chunks)):
            await self._elasticsearch_client.bulk(operations=chunks[i])
            print(f"Chunk {i} of added")
        print("Added to elastic")

    async def update(self, obj_id: str, obj):
        await self._elasticsearch_client.update(index=self._elasticsearch_index, id=obj_id, doc=dict(obj))

    async def delete(self, obj_id: str):
        await self._elasticsearch_client.delete(index=self._elasticsearch_index, id=obj_id)

    async def find_by_atr(self, model: type[BaseModel], atr: str, description: str):
        index_exist = await self._elasticsearch_client.indices.exists(index=self._elasticsearch_index)
        if not index_exist:
            return []
        query = {
            "fuzzy": {
                atr: {
                    "value": description
                }
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
            for hit in hits:
                hit['_source']['id'] = hit['_id']
            priv_result = [
                model.model_validate(hit['_source']) for hit in hits]
            result_list += priv_result
            response = await self._elasticsearch_client.scroll(scroll='1m', scroll_id=scroll_id)
        return result_list
