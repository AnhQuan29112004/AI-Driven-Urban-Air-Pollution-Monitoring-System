class Alias:
    TIME_COLUMN_CANDIDATES = ("timestamp", "datetime", "date", "time", "ds")
    WEATHER_COLUMNS = ("temperature", "humidity", "wind_speed")
    UCI_COLUMN_ALIASES = {
    "co": ("co", "co(gt)", "co_gt"),
    "nox": ("nox", "nox(gt)", "nox_gt"),
    "no2": ("no2", "no2(gt)", "no2_gt"),
    "o3": ("o3", "o3(gt)", "o3_gt"),
    "temperature": ("temperature", "t"),
    "humidity": ("humidity", "rh"),
    "wind_speed": ("wind_speed", "ws"),
    "absolute_humidity": ("absolute_humidity", "ah"),
    "aqi": ("aqi",),
}