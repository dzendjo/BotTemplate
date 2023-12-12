import asyncio
import datetime
from typing import Optional
import os

from bson import ObjectId
from pydantic import Field, BaseModel, HttpUrl
from pymongo import ASCENDING
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, Indexed, init_beanie


class Log(Document):
    class Settings:
        name = "logs"
        indexes = [[("request_date", ASCENDING), ("expireAfterSeconds", 30 * 24 * 60 * 60)]]

    user_id: int
    request_date: datetime.datetime
    text: str


class Advert(Document):
    class Settings:
        name = "adverts"

    date: datetime.datetime = datetime.datetime.now(datetime.UTC)
    name: str
    type: str
    done_users: list[int]
    admin_user_id: int


class User(Document):
    class Settings:
        name = "botusers"

    id: int = Field(None, alias="_id")
    process_flag: bool = False
    created: datetime.datetime
    visited: datetime.datetime
    username: str
    first_name: str
    last_name: str
    language_code: str
    language: str
    is_active: bool = True
    user_from: Indexed(str) | None = None


async def create_indexes():
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_path = f'mongodb://{db_host}:27017'
    client = AsyncIOMotorClient(db_path)
    await init_beanie(database=client['BotDB'],
                      document_models=[Log, User, Advert])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
