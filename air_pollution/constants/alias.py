class Alias:
    TIME_COLUMN_CANDIDATES = ("timestamp", "datetime", "date", "time", "ds")
    POLLUTANT_COLUMNS = ("pm25", "pm10", "no2", "co", "o3", "so2", "aqi")
    WEATHER_COLUMNS = ("temperature", "humidity", "wind_speed")
    UCI_COLUMN_ALIASES = {
    "pm25": ("pm25", "pm2.5", "pm2_5", "pm2_5_aqi"),
    "pm10": ("pm10", "pm10_aqi"),
    "co": ("co", "co(gt)", "co_gt"),
    "nox": ("nox", "nox(gt)", "nox_gt"),
    "no2": ("no2", "no2(gt)", "no2_gt"),
    "o3": ("o3", "o3(gt)", "o3_gt"),
    "so2": ("so2", "so2(gt)", "so2_gt"),
    "temperature": ("temperature", "t"),
    "humidity": ("humidity", "rh"),
    "wind_speed": ("wind_speed", "ws"),
    "absolute_humidity": ("absolute_humidity", "ah"),
    "aqi": ("aqi",),
}
