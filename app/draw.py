from rocketgram import SendMessage, SendVideo, SendAnimation, SendPhoto, SendDocument
from rocketgram import InlineKeyboard
import settings
import asyncio
import httpx
from models import Advert, User
from itertools import chain
from copy import deepcopy


async def get_advert(advert_type):
    # Get advert
    try:
        request_json = {
            'bot_hash': settings.ad_hash,
            'type': advert_type
        }
        advert_dict = {}
        async with httpx.Client() as session:
            async with session.post(settings.api_url_get_advert, json=request_json) as resp:
                resp_json = await resp.json()
                if resp_json['result']:
                    advert_dict = resp_json['advert']

        return advert_dict
    except Exception as e:
        print(e)
        return {}


async def send_advert_to_user(user_id, advert_dict):
    kb = InlineKeyboard()
    if 'buttons' in advert_dict and advert_dict['buttons']:
        for btn_item in advert_dict['buttons']:
            kb.url(btn_item['text'], btn_item['url']).row()

    try:
        if 'media' in advert_dict and 'file_id' in advert_dict['media']:
            if advert_dict['media']['type'] == 'photo':
                await settings.bot.send(SendPhoto(user_id, advert_dict['media']['file_id'],
                                              caption=advert_dict['text'], reply_markup=kb.render()))
            elif advert_dict['media']['type'] == 'video':
                await settings.bot.send(SendVideo(user_id, advert_dict['media']['file_id'],
                                              caption=advert_dict['text'], reply_markup=kb.render()))
            elif advert_dict['media']['type'] == 'animation':
                await settings.bot.send(SendAnimation(user_id, advert_dict['media']['file_id'],
                                                  caption=advert_dict['text'], reply_markup=kb.render()))
            else:
                await settings.bot.send(SendDocument(user_id, advert_dict['media']['file_id'],
                                                 caption=advert_dict['text'], reply_markup=kb.render()))
        else:
            await settings.bot.send(SendMessage(user_id, advert_dict['text'],
                                            disable_web_page_preview=not advert_dict['is_preview_enable'],
                                            reply_markup=kb.render()))
        return True
    except Exception as e:
        print(e)
        return False


async def start_draw(admin_user_id, draw_name):
    # Get users for draw
    draw = await Advert.find_one({'name': draw_name})
    if not draw:
        draw = Advert(name=draw_name, admin_user_id=admin_user_id, type='draw')
        await draw.commit()
    done_users_set = set(draw.done_users)
    all_users_set = set()
    async for user in User.find({'is_active': True}, {}):
        all_users_set.add(user.id)

    users_for_draw = all_users_set.difference(done_users_set)

    advert_dict = await get_advert('draw')
    if not advert_dict:
        await settings.bot.send(SendMessage(admin_user_id, 'Не могу ополучить рекламное сообщение через API'))
        return

    print(advert_dict)
    count = 0
    done_users = []
    for _ in range(len(users_for_draw)):
        count += 1
        user_id = users_for_draw.pop()
        send_result = await send_advert_to_user(user_id, advert_dict)
        done_users.append(user_id)
        if not send_result:
            user = await User.find_one(user_id)
            user.is_active = False
            await user.commit()

        if count == 100:
            draw.done_users = chain(draw.done_users, done_users)
            await draw.commit()
            old_ad_dict = deepcopy(advert_dict)
            advert_dict = await get_advert('draw')
            if not advert_dict:
                await settings.bot.send(SendMessage(admin_user_id, 'Не могу ополучить рекламное сообщение через API'))
                advert_dict = old_ad_dict
            done_users = []
            count = 0
        else:
            await asyncio.sleep(0.1)

    # Send message to admin about and of the draw
    await settings.bot.send(SendMessage(admin_user_id, 'Рассылка закончена!'))


if __name__ == '__main__':
    pass
