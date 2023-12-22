import string
from typing import List, Mapping, Any
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel


class ElasticSearch:
    _elasticsearch_client: AsyncElasticsearch
    _elasticsearch_index: str

    def __init__(self, index: str, elasticsearch_client: AsyncElasticsearch):
        self._elasticsearch_client = elasticsearch_client
        self._elasticsearch_index = index

    async def clear_collection(self, name_of_index):
        name_of_index = self._elasticsearch_index
        try:
            await self._elasticsearch_client.indices.delete(index=name_of_index)
            await self._elasticsearch_client.indices.create(index=name_of_index)
        except Exception as e:
            print(f"Unsuccesfull clear: {e}")
            return "Unsuccess"
        else:
            return "Success"

    async def create(self, obj_id: str, obj: BaseModel):
        await self._elasticsearch_client.create(index=self._elasticsearch_index, id=obj_id, document=dict(obj))

    async def create_many(self, objects_ids: list[str], objects):
        bulk = []
        for i in range(len(objects)):
            # Добавляем операцию index для каждого объекта
            index_operation = {
                'index': {'_index': self._elasticsearch_index, '_id': objects_ids[i]}}
            bulk.append(index_operation)
            bulk.append(objects[i])
        chunk_size = 1000
        chunks = [bulk[i:i + chunk_size]
                  for i in range(0, len(bulk), chunk_size)]
        for chunk in chunks:
            await self._elasticsearch_client.bulk(operations=chunk)
            print(f"Chunk of added")
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
            "bool": {
                "must": [
                    {
                        "fuzzy": {
                            atr: {
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
            for hit in hits:
                hit['_source']['id'] = hit['_id']
            priv_result = [
                model.model_validate(hit['_source']) for hit in hits]
            result_list += priv_result
            response = await self._elasticsearch_client.scroll(scroll='1m', scroll_id=scroll_id)
        return result_list
