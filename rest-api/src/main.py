from fastapi import FastAPI

from handler.event_handlers import startup, shutdown
from router.hosts_router import router as rooms_router
from router.users_router import router as names_router
from router.data_loader_router import router as data_loader_routers

app = FastAPI()

app.include_router(rooms_router, tags=["Rooms"], prefix="/api/rooms")
app.include_router(names_router, tags=["Names"], prefix="/api/users")
app.include_router(data_loader_routers, tags=[
                   "DataLoader"], prefix="/api/data_loader")
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
