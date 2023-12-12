import asyncio
import datetime
from pydantic import HttpUrl
import httpx

from models import User


async def register_user(rg_user):
    now = datetime.datetime.now(datetime.UTC)
    language = 'ua' if rg_user.language_code == 'ua' else 'en'
    user = User(id=rg_user.id,
                created=now,
                visited=now,
                username=rg_user.username,
                first_name=rg_user.first_name,
                last_name=rg_user.last_name,
                language_code=rg_user.language_code,
                language=language)

    await user.insert()
    return user


def split_list(base_list: list, split_count: int) -> list[list]:
    return [base_list[x:x+split_count] for x in range(0, len(base_list), split_count)]


if __name__ == '__main__':
    pass
