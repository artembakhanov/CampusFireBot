import telebot
import redis

from bot.static import *
from bot.timestamps import *

db = redis.Redis(host=REDIS_URL, port=REDIS_PORT, db=0, charset='utf-8', decode_responses=True)
bot = telebot.TeleBot(TOKEN)
last_fire_ts, last_fire_campus_ts, fire_count_campus, fire_count_total, waiting_for_campus = None, None, None, None, None


def launch():
    load_db()
    print('Bot polling...')
    bot.polling()


def load_db():
    global last_fire_ts, last_fire_campus_ts, waiting_for_campus, fire_count_campus, fire_count_total
    last_fire_ts = int(db.get('last_fire_ts')) if db.exists('last_fire_ts') else 0
    last_fire_campus_ts = {i: int(db.get(f'last_fire_campus{i}_ts')) if db.exists(f'last_fire_campus{i}_ts') else 0 for
                           i in range(1, 5)}
    fire_count_total = int(db.get('fire_count_total')) if db.exists('fire_count_total') else 0
    fire_count_campus = {i: int(db.get(f'fire_count_campus{i}')) if db.exists(f'fire_count_campus{i}') else 0 for
                           i in range(1, 5)}
    waiting_for_campus = False
    print('DB loaded.')


def clear_db():
    db.delete('last_fire_ts')
    for i in range(1, 5):
        db.delete(f'last_fire_campus{i}_ts')
    load_db()


def is_on_fire():
    return timestamp_diff_minutes(last_fire_ts, timestamp()) < FIRE_COOLDOWN_MINUTES


@bot.message_handler(commands=["gorim", "fire"], func=lambda m: not is_on_fire())
def fire_handler(message):
    global last_fire_ts, waiting_for_campus, fire_count_total
    last_fire_ts = timestamp()
    db.set('last_fire_ts', last_fire_ts)
    fire_count_total += 1
    db.set('fire_count_total', fire_count_total)
    waiting_for_campus = True
    bot.send_message(message.chat.id, GORIM_LABEL)
    bot.send_message(message.chat.id, WHAT_CAMPUS_LABEL)


@bot.message_handler(content_types=['text'], func=lambda m: (m.text is not None and m.text[0] != '/' and is_on_fire() and waiting_for_campus))
def campus_handler(message):
    global waiting_for_campus, fire_count_campus
    text = message.text.strip().lower()
    campus_id = None
    for test_id in range(1, 5):
        if text in CAMPUS_STRINGS[test_id]:
            campus_id = test_id
            break
    if campus_id is not None:
        waiting_for_campus = False
        last_fire_campus_ts[campus_id] = last_fire_ts
        db.set(f'last_fire_campus{campus_id}_ts', last_fire_ts)
        fire_count_campus[campus_id] += 1
        db.set(f'fire_count_campus{campus_id}', fire_count_campus[campus_id])
        bot.reply_to(message, OK_LABEL)


@bot.message_handler(commands=["stats"])
def stats_handler(message):
    now_ts = timestamp()
    last_fire_campus_id = max(last_fire_campus_ts, key=lambda key: last_fire_campus_ts[key])
    if last_fire_ts == 0:
        bot.send_message(message.chat.id, NO_FIRE_LABEL)
        return
    if last_fire_campus_ts[last_fire_campus_id] == 0:
        stats_message = STATS_GENERAL_LABEL.format(format_time(last_fire_ts, now_ts), fire_count_total)
        bot.send_message(message.chat.id, stats_message)
        return
    most_fires_campus_id = max(fire_count_campus, key=lambda key: fire_count_campus[key])
    stats_message = STATS_LABEL.format(last_fire_campus_id, format_time(last_fire_ts, now_ts), fire_count_total, most_fires_campus_id)
    bot.send_message(message.chat.id, stats_message)


@bot.message_handler(commands=["stats_all"])
def stats_all_handler(message):
    now_ts = timestamp()
    if last_fire_ts == 0:
        bot.send_message(message.chat.id, NO_FIRE_LABEL)
        return
    days_since_last_fire = timestamp_diff_days(last_fire_ts, now_ts)
    most_fires_campus_id = max(fire_count_campus, key=lambda key: fire_count_campus[key])
    stats_message = STATS_ALL_LABEL.format(
        format_timestamp(last_fire_ts), fire_count_total,
        format_time(last_fire_campus_ts[1], now_ts), fire_count_campus[1],
        format_time(last_fire_campus_ts[2], now_ts), fire_count_campus[2],
        format_time(last_fire_campus_ts[3], now_ts), fire_count_campus[3],
        format_time(last_fire_campus_ts[4], now_ts), fire_count_campus[4], most_fires_campus_id, days_since_last_fire)
    bot.send_message(message.chat.id, stats_message)


@bot.message_handler(commands=["reset"], func=lambda m: m.chat.id == ADMIN_ID)
def stats_all_handler(message):
    clear_db()
    bot.send_message(message.chat.id, 'DB reset')