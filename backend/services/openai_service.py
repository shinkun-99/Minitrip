
import json
from openai import OpenAI
from ..config import Config 

client = OpenAI(api_key=Config.OPENAI_API_KEY)


def generate_trip_plan(destination: str, origin: str, 
                       start_date_str: str, end_date_str: str, num_days: int,
                       interests: list, pace: str,  
                       weather_info_for_ai: str, 
                       destination_local_time_str: str = None,
                       other_requirements: str = '',
                       target_language: str = 'en') -> dict:
    interest_str = ", ".join(interests) if interests else "general sightseeing"
    local_time_info = f"目的地 {destination} 的当前当地时间大约是 {destination_local_time_str}。" if destination_local_time_str else ""
    user_custom_requests_prompt_segment = ""
    if other_requirements and other_requirements.strip():
        user_custom_requests_prompt_segment = f"{other_requirements}"
    language_name_map = {
        "en": "English",
        "zh": "Simplified Chinese (简体中文)",
        "ja": "Japanese (日本語)"
    }
    output_language_name = language_name_map.get(target_language.lower(), "English")
    output_language_instruction = f"IMPORTANT: All textual content in your JSON response (including all titles, themes, activity descriptions, reasons, tips, summaries, and daily weather forecasts) MUST be in {output_language_name}."
    
    # 调试日志
    print(f"DEBUG [OPENAI_SERVICE]: Received target_language: {target_language}")
    print(f"DEBUG [OPENAI_SERVICE]: Mapped to output_language_name: {output_language_name}")
    print(f"DEBUG [OPENAI_SERVICE]: Constructed output_language_instruction: {output_language_instruction}")
    
    prompt = f"""
你是 MiniTrip, 一个AI旅行路线推荐助手。
用户希望规划一次旅行。请根据以下信息生成个性化的旅行行程。
{output_language_instruction} 

用户信息:
- 出发地: {origin}
- 目的地: {destination}
- 旅行日期: 从 {start_date_str} 到 {end_date_str} (共 {num_days} 天)
- 兴趣偏好: {interest_str}
- 行程节奏偏好: {pace}
- 用户特殊要求（重要！优先考虑此要求）:{user_custom_requests_prompt_segment}

{local_time_info}

目的地 {destination} 在旅行期间的天气/季节信息如下:
---天气信息开始---
{weather_info_for_ai}
---天气信息结束---

请仔细解读上述天气信息。
- 【重要】如果某天的天气信息中包含具体的每日预报（例如 "日期 YYYY-MM-DD: 天气 X, 温度 Y..."），请将该天的【天气简述】（例如 "小雨, 15-20°C"）提取并放入下面JSON结构中对应日期的 "daily_weather_forecast" 字段。
- 如果某天的天气信息是基于季节的通用建议，可以在 "daily_weather_forecast" 字段中注明是季节性推测，或留空/标记为 "N/A"。
- 根据具体或季节性的天气，调整当天的活动建议。

任务要求:
1.  为这次为期 {num_days} 天的旅行，生成一个多分段的行程。
2.  对于每一天，提供该日的【实际公历日期】（格式<y_bin_46>-MM-DD）、一个【当日主题】、一个【当日天气预报】(如果可用)，然后为【上午】、【下午】、【傍晚/晚上】推荐活动，并附上【推荐理由】。
3.  提供一些与目的地、旅行日期、天气/季节以及用户偏好与用户要求相关的【实用旅行小贴士】
4.  最后，提供一个简短的【行程推荐总结】。

重要输出格式:
请【严格】以单一、有效的 JSON 对象格式返回你的回答，在此JSON对象前后不要有任何其他文本或解释。
JSON 对象应遵循此结构:
{{
  "trip_title": "你的{{num_days}}天{{destination}}之旅 ({{start_date_str}}至{{end_date_str}})",
  "travel_dates_display": "{{start_date_str}} 到 {{end_date_str}}", 
  "destination_local_time_display": "{{如果提供了当地时间, 这里放格式化后的时间字符串, 否则为 'N/A'}}", 
  "destination_weather_summary": "{{根据你收到的天气信息, 为前端生成一个简洁明了的【整体天气小结】, 可换行。这个小结应概括整个行程的天气趋势}}",
  "daily_plans": [
    {{
      "day": 1,
      "date": "{{第一天的实际日期YYYY_MM_DD}}",
      "daily_weather_forecast": "{{当天的天气简述，例如：晴转多云, 20-28°C；或：季节性炎热}}", // <--- 新增字段
      "theme": "{{例如：抵达与城市初探}}",
      "activities": [
        {{"time_slot": "{{上午}}", "activity": "{{例如：抵达，入住酒店，简单午餐。}}", "reason": "{{例如：安顿下来，为接下来的探索做准备。}}"}},
        {{"time_slot": "{{下午}}", "activity": "{{例如：探索当地市中心或一个著名街区。}}", "reason": "{{例如：感受城市氛围，初步了解当地文化。}}"}},
        {{"time_slot": "{{傍晚/晚上}}", "activity": "{{例如：在一家推荐的本地餐馆享用晚餐。}}", "reason": "{{例如：品尝地道美食。}}" }}
      ]
    }}
    // ... 更多天的 daily_plans 对象，每一项都包含 "date" 和 "daily_weather_forecast" 字段 ...
  ],
  "travel_tips": [ /* ... */ ],
  "recommendation_summary": "..."
}}
请确保 JSON 中的所有字符串值都经过正确的转义。
"daily_plans"中每一天的 "date" 字段，请从 {start_date_str} 开始，为旅行的每一天计算出准确的公历日期。
"daily_weather_forecast" 字段应基于你从"天气信息"部分为对应日期提取或总结的天气。
不要在你的回答中包含任何 markdown 格式 (例如 ```json)。
"""


    try:
        print(f"-------------------- PROMPT SENT TO OPENAI --------------------")
        print(prompt)
        print(f"-------------------- END OF PROMPT -------------------------")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "你是一个AI旅行助手，根据用户偏好和详细的天气情境（可能包含具体预报和季节性信息）输出JSON格式的行程计划。"},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4o", 
            response_format={ "type": "json_object" },
            temperature=0.6,
        )
        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)

    except json.JSONDecodeError as e:
        print(f"OpenAI JSON Decode Error: {e}")
        print(f"Raw response attempt: {response_content}")
        return {"error": "AI未能生成有效的行程结构，请稍后重试或调整输入。"}
    except Exception as e:
        print(f"使用OpenAI生成行程时发生错误: {e}")
        return {"error": f"因AI服务错误，无法生成行程计划: {str(e)}"}