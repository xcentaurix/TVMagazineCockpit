# !/usr/bin/python
# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import time
import calendar
from datetime import datetime, timedelta
from .Debug import logger


def iso_to_epoch(iso_string):
    """Convert ISO 8601 timestamp to seconds since epoch."""
    if not iso_string:
        return 0

    try:
        # Handle basic ISO format (removing any milliseconds)
        # Format: YYYY-MM-DDTHH:MM:SS
        iso_parts = iso_string.replace(',', '.').split('.')
        base_time = iso_parts[0]

        # Find where the timezone indicator starts
        tz_pos = -1
        for i, char in enumerate(base_time):
            if char in {'+', '-'} and i > 10:  # Must be after date portion
                tz_pos = i
                break

        # If no explicit timezone indicator found
        if tz_pos == -1:
            if 'Z' in base_time:
                # UTC time
                dt = datetime.strptime(base_time.replace(
                    'Z', ''), "%Y-%m-%dT%H:%M:%S")
                return calendar.timegm(dt.utctimetuple())
            # No timezone info, assume local time
            dt = datetime.strptime(base_time, "%Y-%m-%dT%H:%M:%S")
            return calendar.timegm(dt.utctimetuple())

        # Extract time and timezone offset
        time_part = base_time[:tz_pos]
        offset_part = base_time[tz_pos:]

        # Parse the date and time
        dt = datetime.strptime(time_part, "%Y-%m-%dT%H:%M:%S")

        # Parse timezone offset
        sign = offset_part[0]
        if ':' in offset_part:
            # Format: +HH:MM or -HH:MM
            hours, minutes = offset_part[1:].split(':')
        elif len(offset_part) >= 3:
            # Format: +HHMM or -HHMM
            hours = offset_part[1:3]
            minutes = offset_part[3:5] if len(offset_part) >= 5 else "00"
        else:
            # Unknown format
            logger.error("Unknown timezone format: %s", offset_part)
            hours, minutes = "00", "00"

        offset_seconds = int(hours) * 3600 + int(minutes) * 60

        # Apply timezone offset
        if sign == '+':
            dt = dt - timedelta(seconds=offset_seconds)
        else:
            dt = dt + timedelta(seconds=offset_seconds)

        return calendar.timegm(dt.utctimetuple())

    except Exception as e:
        logger.error("Failed to parse ISO time: %s - %s", iso_string, e)
        return 0


def datetime_to_epoch(datetime_str):
    """Convert datetime string in format 'YYYY-MM-DD HH:MM:SS' to epoch seconds"""
    if not datetime_str:
        return 0

    try:
        # Parse the datetime string
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

        # Determine if we're in daylight saving time (rough approximation for CET/CEST)
        # Last Sunday of March to last Sunday of October is typically CEST
        year = dt.year
        is_summer_time = False

        # Simplified DST check - this is an approximation
        if dt.month > 3 and dt.month < 10:
            is_summer_time = True
        elif dt.month == 3:
            # Check if it's after the last Sunday of March
            last_day = 31
            while datetime(year, 3, last_day).weekday() != 6:  # 6 is Sunday
                last_day -= 1
            is_summer_time = dt.day >= last_day
        elif dt.month == 10:
            # Check if it's before the last Sunday of October
            last_day = 31
            while datetime(year, 10, last_day).weekday() != 6:  # 6 is Sunday
                last_day -= 1
            is_summer_time = dt.day < last_day

        # Apply the timezone offset (UTC+1 for winter, UTC+2 for summer)
        hours_offset = 2 if is_summer_time else 1
        dt = dt - timedelta(hours=hours_offset)

        # Convert to timestamp (as UTC)
        return calendar.timegm(dt.utctimetuple())
    except Exception as e:
        logger.error("Error converting datetime: %s - %s", datetime_str, e)
        return 0


def timestamp_to_day_int(timestamp):
    """
    Get Unix timestamp for midnight (0:00) of the day represented by the given timestamp.

    Args:
        timestamp (int): Unix timestamp for any time during a day

    Returns:
        int: Unix timestamp for midnight (0:00) of the same day
    """
    # Convert timestamp to local time struct
    time_struct = time.localtime(timestamp)

    # Create a new time struct for midnight (0:00) of the same day
    midnight_time = time.struct_time((
        time_struct.tm_year,   # Year
        time_struct.tm_mon,    # Month
        time_struct.tm_mday,   # Day
        0,                     # Hour (00)
        0,                     # Minute (00)
        0,                     # Second (00)
        time_struct.tm_wday,   # Weekday
        time_struct.tm_yday,   # Day of year
        time_struct.tm_isdst   # DST flag
    ))

    # Convert to epoch timestamp
    day_int = int(time.mktime(midnight_time))

    logger.debug("day_int: %s", day_int)
    return day_int


def get_day_details(day_index):
    """
    Get details for a specific day in the TV magazine.
    Args:
        day_index (int): Index of the day (0 for today, 1 for tomorrow, etc.)
    Returns:
        tuple: (date_str, day_int)
            - date_str: Formatted date string (e.g., "2023-10-01")
            - day_int: Unix timestamp for midnight of that day
    """
    yesterday = datetime.now() - timedelta(days=1)  # Start from yesterday
    target_date = yesterday + timedelta(days=day_index)

    # Format date string
    date_str = target_date.strftime("%Y-%m-%d")

    # Get midnight epoch timestamp - compatible with older Python versions
    target_midnight = target_date.replace(
        hour=0, minute=0, second=0, microsecond=0)
    day_int = int(time.mktime(target_midnight.timetuple()))

    logger.debug("date_str: %s, day_int: %s", date_str, day_int)
    return date_str, day_int
