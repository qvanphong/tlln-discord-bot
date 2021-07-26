from src.utils import env


def get_channel_id(name):
    name = name.lower()

    if name == 'neo':
        return env.NEO_CHANNEL
    if name == 'firo':
        return env.FIRO_CHANNEL
    if name == 'btc':
        return env.BTC_CHANNEL
    if name == 'zen':
        return env.ZEN_CHANNEL
    if name == 'dash':
        return env.DASH_CHANNEL
    if name == 'ark':
        return env.ARK_CHANNEL
    if name == 'gas':
        return env.NEO_CHANNEL


def get_server_tlln_id():
    return env.SERVER_ID


def get_spam_bot_channel_id():
    return env.SPAM_BOT_CHANNEL
