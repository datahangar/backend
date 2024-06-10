from fastapi import APIRouter
from routes.turnilo_dashboard_routes import turnilo_router

api_router = APIRouter()
api_router.include_router(turnilo_router)
