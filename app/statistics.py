from io import BytesIO
import orjson

from models import User
from mybot import router
from rocketgram import commonfilters, ChatType, SendMessage, commonwaiters, InputFile, SendDocument, DeleteMessage
from rocketgram import context
import settings


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/base')
async def start_command():
    if context.user.id not in settings.admins:
        await SendMessage(context.user.id, context.message.text, reply_to_message_id=context.message.message_id).send()
        return

    count = await User.count()
    await SendMessage(context.user.id, str(count)).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/cleanbase')
async def start_message():
    if context.user.id not in settings.admins:
        await SendMessage(context.user.id, context.message.text, reply_to_message_id=context.message.message_id).send()
        return

    num_non_active = await User.find(User.is_active == False).count()
    mt = f'To delete {num_non_active} non active users type - yes.'
    await SendMessage(context.user.id, mt).send()

    yield commonwaiters.next_message()
    if context.message.text.lower() == 'yes':
        del_res = await User.find(User.is_active == False).delete()
        mt = f'{del_res.deleted_count} non active users is removed!'
        await SendMessage(context.user.id, mt).send()
    else:
        mt = 'Removing is cancelled'
        await SendMessage(context.user.id, mt).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/getbase')
async def get_base():
    if context.user.id not in settings.admins:
        await SendMessage(context.user.id, context.message.text, reply_to_message_id=context.message.message_id).send()
        return

    users = []

    load_message = await SendMessage(context.user.id, 'File is loading, wait a little...').send()

    async for user in User.all():
        users.append(user.id)

    file_json = InputFile(
        file_name=f'{context.bot.name}.json',
        content_type='application/json',
        data=BytesIO(orjson.dumps(users))
    )

    await SendDocument(context.user.id, file_json).send()
    await DeleteMessage(context.user.id, load_message.message_id).send()
