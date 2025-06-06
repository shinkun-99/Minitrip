import requests
from ..config import Config
from datetime import datetime, date, timedelta, timezone

API_KEY = Config.OPENWEATHER_API_KEY


GEOCODING_BASE_URL = "http://api.openweathermap.org/geo/1.0/direct"
CURRENT_WEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

# 可精准预测天气温度范围为7日内，超过7日则仅输出通用季节性建议
# 当前版本代码可在后端控制台输出内容，用于debug


FAR_TERM_THRESHOLD_DAYS = 7 
ONE_CALL_FORECAST_SPAN_DAYS = 8 

# 读取前端输入的目的地城市，处理天气数据并返回

# 将城市名转换为经纬度
def get_lat_lon_from_city(city_name: str):

    if not API_KEY:
        print("错误：API Key 未在配置中设置。")
        return None, None
    params = {
        "q": city_name, 
        "limit": 1, 
        "appid": API_KEY
    }
    print(f"天气服务：正在为城市 '{city_name}' 获取经纬度...")
    try:
        response = requests.get(GEOCODING_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data and len(data) > 0:
            print(f"天气服务：获取到经纬度: Latitude={data[0]['lat']}, Longitude={data[0]['lon']}")
            return data[0]["lat"], data[0]["lon"]
        print(f"天气服务错误：找不到城市 '{city_name}' 的经纬度。API 响应: {data}")
        return None, None
    except requests.exceptions.HTTPError as http_err:
        print(f"天气服务：地理编码 API HTTP 错误: {http_err}")
        try: print(f"天气服务：地理编码 API 错误响应体: {response.text}")
        except: pass
        return None, None
    except Exception as e:
        print(f"天气服务：解析地理编码响应时发生意外错误: {e}")
        return None, None

# 获取目的地的当前当地时间和时区偏移
def get_current_local_time_and_timezone_offset(lat, lon):

    if not API_KEY or lat is None or lon is None: return "N/A", "N/A", None
    params = {
        "lat": lat, 
        "lon": lon, 
        "appid": API_KEY, 
        "units": "metric"}
    try:
        response = requests.get(CURRENT_WEATHER_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "timezone" in data:
            offset_seconds = data["timezone"]
            current_utc = datetime.now(timezone.utc)
            local_time = current_utc + timedelta(seconds=offset_seconds)
            return local_time.strftime('%Y-%m-%d %H:%M:%S %Z%z'), local_time.strftime('%I:%M %p, %b %d'), offset_seconds
        return "N/A", "N/A", None
    except Exception as e:
        print(f"天气服务：获取当前时间错误 for lat/lon {lat}/{lon}: {e}")
        return "N/A", "N/A", None

#获取 One Call API 返回的原始 daily 数组数据 (未来8天，包括今天)
def get_onecall_8day_raw_data(lat: float, lon: float):

    if not API_KEY or lat is None or lon is None: return None
    params = {
        "lat": lat, "lon": lon, "exclude": "current,minutely,hourly,alerts",
        "appid": API_KEY, "units": "metric", "lang": "zh_cn"
    }
    print(f"天气服务：正在为坐标 ({lat}, {lon}) 获取未来8天每日天气预报原始数据 (使用 One Call API)...")
    try:
        response = requests.get(CURRENT_WEATHER_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        daily_data = data.get("daily")
        if daily_data:
            print(f"天气服务：成功获取 {len(daily_data)} 天的原始每日预报数据。")
        else:
            print(f"天气服务错误：One Call API响应中未找到 'daily' 数据。完整响应：{data}")
        return daily_data 
    except requests.exceptions.HTTPError as http_err:
        print(f"天气服务：OneCall API HTTP 错误 (原始数据获取): {http_err}")
        try: print(f"天气服务：OneCall API 错误响应体: {response.text}")
        except: pass
        return None
    except Exception as e:
        print(f"天气服务：获取 OneCall 原始数据时发生错误: {e}")
        return None


#格式化单日的原始预报数据，供ai模型和前端显示使用
def format_daily_forecast_for_one_day(day_data, target_date: date):

    date_str_display_full = target_date.strftime("%Y-%m-%d (%A)")

    temp_min = day_data.get("temp", {}).get("min", "N/A")
    temp_max = day_data.get("temp", {}).get("max", "N/A")
    temp_day_actual = day_data.get("temp", {}).get("day", "N/A")
    weather_array = day_data.get("weather", [])
    weather_description = weather_array[0]["description"] if weather_array else "N/A"
    humidity = day_data.get("humidity", "N/A")
    pop = int(day_data.get("pop", 0) * 100)

    ai_summary = (
        f"日期 {target_date.strftime('%Y-%m-%d')}: 天气 {weather_description}, "
        f"温度范围 {temp_min}°C 至 {temp_max}°C (日间约 {temp_day_actual}°C), "
        f"湿度 {humidity}%, 降水概率 {pop}%."
    )

    display_summary = (f"{date_str_display_full}:\n"
                       f"  天气: {weather_description}\n"
                       f"  温度: {temp_min}°C - {temp_max}°C (日间: {temp_day_actual}°C)\n"
                       f"  湿度: {humidity}%, 降水概率: {pop}%")
    return {"for_ai": ai_summary, "for_display": display_summary}


# 根据月份生成通用季节性建议
def generate_seasonal_advice_for_month(destination_city: str, target_date: date):

    month_name = target_date.strftime("%B")
    month_num = target_date.month
    season = ""

    if month_num in [12, 1, 2]: season = "冬季"
    elif month_num in [3, 4, 5]: season = "春季"
    elif month_num in [6, 7, 8]: season = "夏季"
    elif month_num in [9, 10, 11]: season = "秋季"

    ai_advice = f"对于 {target_date.strftime('%Y-%m-%d')} ({month_name}) 在 {destination_city} 的行程: "
    display_advice = f"{target_date.strftime('%Y-%m-%d (%A)')} ({month_name}): "

    if season:
        ai_advice += f"当地通常是{season}。 "
        display_advice += f"通常是{season}。"
        if season == "夏季":
            ai_advice += "气温较高，请注意防暑降温，建议穿着轻便透气的衣物，并做好防晒。户外活动请避开正午高温时段。"
            display_advice += " 气温较高，注意防晒。 "
        elif season == "冬季":
            ai_advice += "气温较低，请注意保暖，建议穿着厚实的衣物，如羽绒服、帽子、手套等。室内外温差可能较大。"
            display_advice += " 气温较低，注意保暖。 "
        elif season == "春季":
            ai_advice += "天气多变，早晚温差可能较大，建议携带方便穿脱的衣物，并可能偶有春雨。"
            display_advice += " 天气多变，注意添衣。 "
        elif season == "秋季":
            ai_advice += "天气通常较为宜人，但早晚可能转凉，建议准备外套。是户外活动的好时节。"
            display_advice += " 天气宜人，早晚可能转凉。 "
    else:
        ai_advice += "请参考当地该月份的典型气候特征进行规划。 "
        display_advice += "请参考当地典型气候。 "
    
    ai_advice += "由于这是基于季节的通用建议，具体天气请在临近出行时再次确认。"
    display_advice += " (通用季节性建议，临近时请查阅详细预报)"
    return {"for_ai": ai_advice, "for_display": display_advice}

# 获取行程期间的天气信息（详细或季节性）和目的地当前时间。
def get_weather_and_time_for_trip(destination_city: str, start_date: date, end_date: date) -> dict:

    output = {
        "weather_summary_for_ai": "未能获取到具体天气信息，请AI基于通用知识提供建议。", 
        "weather_display": "未能获取到行程期间的详细天气信息。",
        "destination_local_time_display": "N/A",
        "destination_local_time_raw": None,
        "travel_dates_display": f"{start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}"
    }

    if not API_KEY:
        output["weather_summary_for_ai"] = "天气服务未配置API Key。"
        output["weather_display"] = "天气服务未配置。"
        return output

    lat, lon = get_lat_lon_from_city(destination_city)
    if lat is None or lon is None:
        output["weather_summary_for_ai"] = f"无法找到城市 '{destination_city}' 的位置信息。"
        output["weather_display"] = f"找不到城市 '{destination_city}'。"
        return output
        
    raw_local_time_str, local_time_display_str, _ = get_current_local_time_and_timezone_offset(lat, lon)
    output["destination_local_time_display"] = local_time_display_str
    output["destination_local_time_raw"] = raw_local_time_str if raw_local_time_str != "N/A" else None

    today = date.today()
    days_until_trip_start = (start_date - today).days
    trip_duration_days = (end_date - start_date).days + 1

    list_of_weather_for_ai = []
    list_of_weather_for_display = []

    if days_until_trip_start < 0 and abs(days_until_trip_start) < ONE_CALL_FORECAST_SPAN_DAYS:
        print(f"天气服务：行程起始日 {start_date} 早于或等于今天 {today}，但仍在近期预报范围内。")
        pass


    if days_until_trip_start > FAR_TERM_THRESHOLD_DAYS: 
        print(f"天气服务：远期出行 (在 {days_until_trip_start} 天后开始)。")
        seasonal_advice = generate_seasonal_advice_for_month(destination_city, start_date)
        output["weather_summary_for_ai"] = f"这是一次远期规划的旅行。\n{seasonal_advice['for_ai']}"
        output["weather_display"] = seasonal_advice['for_display']
    else: 
        print(f"天气服务：近期出行 (在 {days_until_trip_start} 天后开始)。获取详细预报...")
        raw_8day_forecasts_from_today = get_onecall_8day_raw_data(lat, lon)

        if not raw_8day_forecasts_from_today:
            print("天气服务错误：无法获取到8天原始预报数据，将使用通用季节性建议。")
            seasonal_advice = generate_seasonal_advice_for_month(destination_city, start_date)
            output["weather_summary_for_ai"] = f"未能获取详细天气预报。\n{seasonal_advice['for_ai']}"
            output["weather_display"] = seasonal_advice['for_display']
            return output

        for i in range(trip_duration_days):
            current_trip_date = start_date + timedelta(days=i)
            offset_from_today_for_this_trip_date = (current_trip_date - today).days

            if 0 <= offset_from_today_for_this_trip_date < ONE_CALL_FORECAST_SPAN_DAYS and \
               offset_from_today_for_this_trip_date < len(raw_8day_forecasts_from_today):
                day_data = raw_8day_forecasts_from_today[offset_from_today_for_this_trip_date]
                formatted_day = format_daily_forecast_for_one_day(day_data, current_trip_date)
                list_of_weather_for_ai.append(formatted_day["for_ai"])
                list_of_weather_for_display.append(formatted_day["for_display"])
            else:
                seasonal_day_advice = generate_seasonal_advice_for_month(destination_city, current_trip_date)
                list_of_weather_for_ai.append(seasonal_day_advice["for_ai"])
                list_of_weather_for_display.append(seasonal_day_advice["for_display"])

        if list_of_weather_for_ai:
            output["weather_summary_for_ai"] = "行程期间天气展望：\n" + "\n".join(list_of_weather_for_ai)
        if list_of_weather_for_display:
            output["weather_display"] = "\n".join(list_of_weather_for_display)
        
        if not list_of_weather_for_ai and not list_of_weather_for_display:
             seasonal_fallback = generate_seasonal_advice_for_month(destination_city, start_date)
             output["weather_summary_for_ai"] = seasonal_fallback["for_ai"]
             output["weather_display"] = seasonal_fallback["for_display"]
             
    return output