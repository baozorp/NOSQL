from fastapi import FastAPI

from handler.event_handlers import startup, shutdown
from router.hosts_router import router as hosts_router
from router.users_router import router as users_router
from router.data_loader_router import router as data_loader_routers
from router.reservations_router import router as reservations_router

app = FastAPI()

app.include_router(hosts_router, tags=["Rooms"], prefix="/api/rooms")
app.include_router(users_router, tags=["Names"], prefix="/api/users")
app.include_router(data_loader_routers, tags=[
                   "DataLoader"], prefix="/api/data_loader")
app.include_router(reservations_router, tags=[
                   "DataLoader"], prefix="/api/reservations")
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)
