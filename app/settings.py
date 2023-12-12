from j2tools import YamlLoader
from jinja2 import Environment
from contextvars import ContextVar
from rocketgram import Bot

jinja = Environment(loader=YamlLoader('templates/ua.yaml'))

admins = []

bot_name = 'bot_name'
bot: Bot | None = None

current_T = ContextVar('current_T')
get_t = None

current_user = ContextVar('current_user')

ad_hash = 'ad_hash'

api_url_available_campaigns = 'https://adbotapi.fastbots.net/available-campaigns'
api_url_get_advert = 'https://adbotapi.fastbots.net/get-advert'


