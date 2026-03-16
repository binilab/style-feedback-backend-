from fastapi import FastAPI

from app.api.router import api_router 
from app.core.config import settings 
from app.core.database import engine,Base 
from app.domain.user import models as user_models 


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)


@app.on_event('startup')
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(api_router)