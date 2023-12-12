from rocketgram import SendMessage
from rocketgram import commonfilters, ChatType, context, AnswerCallbackQuery

import settings
from models import User
from mybot import router


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('set_lang')
async def set_lang():
    await AnswerCallbackQuery(context.update.callback_query.id).send()

    lang = context.update.callback_query.data.split()[-1]
    user = settings.current_user.get()

    await user.set({User.language: lang})

    T = settings.get_t(user.language)
    settings.current_T.set(T)

    await SendMessage(context.user.id, T('start/mt')).send()
