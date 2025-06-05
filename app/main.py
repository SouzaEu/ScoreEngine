import logging
from fastapi import FastAPI
from .api.v1.api import api_router
from .core.config import get_settings

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

app = FastAPI(title="Lynex Score Engine")
app.include_router(api_router, prefix="/v1")
logger.info("Lynex Score Engine initialized")

@app.get("/")
def read_root():
    return {"message": "Lynex Score Engine"}
