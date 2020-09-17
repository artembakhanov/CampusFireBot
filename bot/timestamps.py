from datetime import datetime

from bot.static import *


def timestamp():
    return int(datetime.now().timestamp())


def datetime_from_timestamp(ts):
    return datetime.fromtimestamp(ts)


def timestamp_diff_days(a, b):
    return int((b-a) / (3600 * 24))


def timestamp_diff_minutes(a, b):
    return int((b-a) / 60)


def get_last_fire_data(ts):
    last_fire_datetime = datetime_from_timestamp(ts)
    days_since_last_fire = timestamp_diff_days(ts, timestamp())
    return last_fire_datetime, days_since_last_fire


def format_time_since(time_unit, format_table):
    if time_unit // 10 % 10 == 1:
        return format_table[0].format(time_unit)
    if time_unit % 10 == 1:
        return format_table[2].format(time_unit)
    if 1 < time_unit % 10 < 5:
        return format_table[1].format(time_unit)
    return format_table[0].format(time_unit)


def format_days(days):
    return format_time_since(days, DAYS_SINCE_FORMATS)


def format_hours(hours):
    return format_time_since(hours, HOURS_SINCE_FORMATS)


def format_minutes(minutes):
    return format_time_since(minutes, MINUTES_SINCE_FORMATS)


def format_seconds(seconds):
    return format_time_since(seconds, SECONDS_SINCE_FORMATS)


def format_time(ts, now_ts):
    if ts > 0:
        diff_seconds = now_ts - ts
        if diff_seconds < 60:
            return format_seconds(diff_seconds)
        elif diff_seconds < 3600:
            return format_minutes(int(diff_seconds / 60))
        elif diff_seconds < 3600 * 24:
            return format_hours(int(diff_seconds / 3600))
        else:
            return format_days(int(diff_seconds / (3600 * 24)))
    return NO_TIME_LABEL


def format_timestamp(ts):
    if ts > 0:
        return datetime_from_timestamp(ts).strftime(TIME_FORMAT)
    return NO_TIME_LABEL
