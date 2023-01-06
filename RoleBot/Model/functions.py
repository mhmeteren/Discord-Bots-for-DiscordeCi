import json

with open('./BotSettings/settings.json', 'r', encoding='utf-8') as f:
    settings = json.loads(f.read())

with open('./BotSettings/settings_api.json', 'r', encoding='utf-8') as f:
    settings_api = json.loads(f.read())
