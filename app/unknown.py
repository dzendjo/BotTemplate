from app.mybot import router
from rocketgram import commonfilters, ChatType, SendMessage, priority, MessageType
from rocketgram import context
from pprint import pp


@router.handler
@commonfilters.chat_type(ChatType.private)
@priority(2050)
def unknown():
    """\
    This is about how to use priority.
    This handler caches all messages to bot, but since we set priority
    to 2048 handler will be called if no other handlers was do.
    Default priority in Dispatcher is 1024, so for
    set the order of handlers you can use @priority decorator."""

    SendMessage(context.user.id,
                "Do not know this command 👻").webhook()


@router.handler
@commonfilters.message_type(MessageType.video)
def unknown():
    pp(context.update.message)


@router.handler
@commonfilters.message_type(MessageType.photo)
def unknown():
    pp(context.update.message)


@router.handler
@commonfilters.message_type(MessageType.document)
def unknown():
    pp(context.update.message)
