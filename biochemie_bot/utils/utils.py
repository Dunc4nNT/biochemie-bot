from datetime import timedelta


def format_timedelta(time: timedelta) -> str:
    """Format a :class:`timedelta` into a human-readable format.

    The format: `x day(s), y hour(s), z minute(s), z2 second(s)`.

    Parameters
    ----------
    time : timedelta
        The timedelta to format.

    Returns
    -------
    str
        The formatted timedelta.
    """
    seconds_in_a_minute = 60
    seconds_in_an_hour = seconds_in_a_minute * 60
    seconds_in_a_day = seconds_in_an_hour * 24

    days, remainder = divmod(time.seconds, seconds_in_a_day)
    hours, remainder = divmod(remainder, seconds_in_an_hour)
    minutes, seconds = divmod(remainder, seconds_in_a_minute)

    days_str = f"{days} day" if days == 1 else f"{days} days"
    hours_str = f"{hours} hour" if hours == 1 else f"{hours} hours"
    minutes_str = f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
    seconds_str = f"{seconds} second" if seconds == 1 else f"{seconds} seconds"

    if time.seconds >= seconds_in_a_day:
        return f"{days_str}, {hours_str}, {minutes} and {seconds_str}"
    if time.seconds >= seconds_in_an_hour:
        return f"{hours_str}, {minutes_str} and {seconds_str}"
    if time.seconds >= seconds_in_a_minute:
        return f"{minutes_str} and {seconds_str}"
    return seconds_str
