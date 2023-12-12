import logging
import os
import asyncio

import statistics
import callbacks
import commands
import keyboards
import mybot
import rocketgram
import settings
from templates import templates
import models

import j2tools
import jinja2
import jinja2.ext


logger = logging.getLogger('minibots.engine')


def main():
    mode = os.environ.get('MODE')
    if mode is None and 'DYNO' in os.environ:
        mode = 'heroku'

    if mode not in ('updates', 'webhook', 'heroku'):
        raise TypeError('MODE must be `updates` or `webhook` or `heroku`!')

    logging.basicConfig(format='%(asctime)s - %(levelname)-5s - %(name)-25s: %(message)s')
    logging.basicConfig(level=logging.ERROR)
    logging.getLogger('engine').setLevel(logging.INFO)
    logging.getLogger('mybot').setLevel(logging.DEBUG)
    logging.getLogger('rocketgram').setLevel(logging.DEBUG)
    logging.getLogger('rocketgram.raw.in').setLevel(logging.INFO)
    logging.getLogger('rocketgram.raw.out').setLevel(logging.INFO)

    logger.info('Starting bot''s template in %s...', mode)

    settings.bot = mybot.get_bot(os.environ['TOKEN'].strip())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(models.create_indexes())

    _loader = jinja2.PrefixLoader({k: j2tools.YamlLoader(v) for k, v in templates.items()})
    _jinja = jinja2.Environment(loader=_loader)

    # Register jinja filters if need:
    pass

    settings.get_t = j2tools.t_factory(_jinja)

    if mode == 'updates':
        rocketgram.UpdatesExecutor.run(settings.bot, drop_pending_updates=bool(int(os.environ.get('DROP_UPDATES', 0))))
    else:
        port = int(os.environ['PORT']) if mode == 'heroku' else int(os.environ.get('WEBHOOK_PORT', 8080))
        rocketgram.AioHttpExecutor.run(settings.bot,
                                       os.environ['WEBHOOK_URL'].strip(),
                                       os.environ.get('WEBHOOK_PATH', '/').strip(),
                                       host='0.0.0.0', port=port,
                                       drop_pending_updates=bool(int(os.environ.get('DROP_UPDATES', 0))),
                                       webhook_remove=not mode == 'heroku')
    logger.info('Bye!')


if __name__ == '__main__':
    main()

