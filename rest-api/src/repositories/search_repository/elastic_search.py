from typing import List, Mapping, Any
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel


class ElsaticSearch:
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

    async def create(self, student_id: str, student: BaseModel):
        await self._elasticsearch_client.create(index=self._elasticsearch_index, id=student_id, document=dict(student))

    async def create_many(self, objects_ids: list[str], objects):
        bulk = []
        for i in range(len(objects)):
            # Добавляем операцию index для каждого объекта
            index_operation = {
                'index': {'_index': self._elasticsearch_index, '_id': objects_ids[i]}}
            bulk.append(index_operation)
            bulk.append(objects[i])
        chunks = [bulk[i:i + 5000] for i in range(0, len(bulk), 5000)]
        for chunk in chunks:
            await self._elasticsearch_client.bulk(operations=chunk)

    async def update(self, student_id: str, student):
        await self._elasticsearch_client.update(index=self._elasticsearch_index, id=student_id, doc=dict(student))

    async def delete(self, student_id: str):
        await self._elasticsearch_client.delete(index=self._elasticsearch_index, id=student_id)

    async def find_by_name(self, name: str):
        index_exist = await self._elasticsearch_client.indices.exists(index=self._elasticsearch_index)

        if not index_exist:
            return []
        query = {
            "bool": {
                "must": [
                    {
                        "match": {
                            "description": name
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
