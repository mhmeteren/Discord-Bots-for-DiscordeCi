import json

with open('./settings/settings_bot.json', 'r', encoding='utf-8') as f:
    settings_bot = json.loads(f.read())
