from beanie import init_beanie
import motor.motor_asyncio

from app import models


async def init_db(mongo_uri):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        mongo_uri
    )

    await init_beanie(database=client.db_name, document_models=[models.User, models.Route])
