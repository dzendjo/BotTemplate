import asyncio
import re
import datetime
from pydantic import HttpUrl
from pprint import pp
import random

import httpx
from rocketgram import InlineKeyboard, EditMessageText, Bot
from rocketgram import SendMessage, DeleteMessage, UpdateType, MessageType
from rocketgram import commonfilters, ChatType, context, SendAnimation, commonwaiters

from draw import start_draw
from models import User
from mybot import router
import settings

url_pattern = re.compile(r'(?P<url>https?://[^\s]+)')


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/draw')
async def start_message():
    if context.user.id not in settings.admins:
        await SendMessage(context.user.id, context.message.text, reply_to_message_id=context.message.message_id).send()
        return

    T = settings.current_T.get()

    async with httpx.Client() as session:
        body = {"bot_hash": settings.ad_hash, "type": "draw"}
        available_campaigns = {}
        async with session.post(settings.api_url_available_campaigns, json=body) as resp:
            resp_json = await resp.json()
            if resp_json['result']:
                available_campaigns = resp_json['available-campaigns']
            else:
                await SendMessage(context.user.id, resp_json['error']).send()
                return

    print(available_campaigns)
    total = 0
    for campaign_name, item in available_campaigns.items():
        total += item['ordered_count'] - item['done_count']
    mt = T('draw/mt', campaigns=available_campaigns, total=total)
    await SendMessage(context.user.id, mt).send()

    yield commonwaiters.next_message()

    if context.message.text == 'start':
        # Create task for draw
        asyncio.create_task(start_draw(context.user.id, list(available_campaigns.keys())[0]))
        await SendMessage(context.user.id, T('draw/start_draw_mt')).send()
    else:
        await SendMessage(context.user.id, T('draw/not_start_draw_mt')).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/start')
async def start_message():
    utm = context.message.text.split()[-1]
    if utm:
        user = settings.current_user.get()
        await user.set({User.user_from: utm})

    mt = 'Choose your language:'

    kb = InlineKeyboard()
    kb.callback('🇺🇦 Українська', 'set_lang ua')
    kb.callback('🇺🇸 English', 'set_lang en')
    kb.arrange_simple(2)

    await SendMessage(context.user.id, mt, reply_markup=kb.render()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/help')
async def start_message():
    T = settings.current_T.get()
    await SendMessage(context.user.id, T('help'), disable_web_page_preview=True).send()


@router.handler
@commonfilters.update_type(UpdateType.message)
@commonfilters.message_type(MessageType.text)
@commonfilters.chat_type(ChatType.private)
async def text_message():
    T = settings.current_T.get()
    user = settings.current_user.get()

    await SendMessage(user.id, context.message.text, reply_to_message_id=context.message.message_id).send()


@router.handler
@commonfilters.message_type(MessageType.animation)
@commonfilters.chat_type(ChatType.private)
async def animation_message():
    T = settings.current_T.get()
    user = settings.current_user.get()

    pp(context.message)
    print(context.message.animation.file_id)

