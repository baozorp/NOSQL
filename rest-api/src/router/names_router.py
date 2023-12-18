from typing import Any, List
from fastapi import APIRouter, Depends

# from repository.repository import Repository


routersa = APIRouter()


@routersa.get("/")
async def get_all_hosts() -> list[str]:
    return ["Hello,", "world!"]
