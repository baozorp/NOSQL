from fastapi import FastAPI

from handler.event_handlers import startup, shutdown
from router.hosts_router import router as rooms_router
from router.names_router import router as names_router

app = FastAPI()

app.include_router(rooms_router, tags=["Rooms"], prefix="/api/rooms")
app.include_router(names_router, tags=["names"], prefix="/api/names")
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
