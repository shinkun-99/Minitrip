from flask import Blueprint, request, jsonify
from ..services import weather_service, openai_service 
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "MiniTrip backend is running!"}), 200

@api_bp.route('/plan-trip', methods=['POST'])
def plan_trip():
    data = request.json
    if not data: 
        return jsonify({"error": "No data provided"}), 400

    destination = data.get('destination')
    origin = data.get('origin', 'N/A')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    interests = data.get('interests', [])
    pace = data.get('pace', 'moderate')
    other_requirements = data.get('other_requirements', '')
    target_language = data.get('target_language', 'en')
    
    print(f"DEBUG [ROUTES]: Received target_language from frontend: {target_language}") 

    if not all([destination, start_date_str, end_date_str]):
        return jsonify({"error": "Missing required fields: destination, start_date, end_date"}), 400
    
    try:
        start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        if start_date_obj > end_date_obj:
            return jsonify({"error": "Start date must be before or same as end date."}), 400
        num_days = (end_date_obj - start_date_obj).days + 1
        if num_days <= 0:
             return jsonify({"error": "Invalid date range, number of days must be positive."}), 400
        if num_days > 30: 
            return jsonify({"error": "Trip duration cannot exceed 30 days."}), 400
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use yyyy-MM-DD."}), 400

    weather_data_dict = weather_service.get_weather_and_time_for_trip(
        destination_city=destination, 
        start_date=start_date_obj,
        end_date=end_date_obj
    )
    
    weather_info_for_ai_prompt = weather_data_dict.get("weather_summary_for_ai", 
                                                       "Weather information could not be determined. Please plan generally.")
    
    trip_plan_json = openai_service.generate_trip_plan(
        destination=destination,
        origin=origin,
        start_date_str=start_date_str,
        end_date_str=end_date_str,
        num_days=num_days,
        interests=interests,
        pace=pace,
        weather_info_for_ai=weather_info_for_ai_prompt,
        destination_local_time_str=weather_data_dict.get("destination_local_time_raw"),
        other_requirements=other_requirements,
        target_language=target_language
    )

    if trip_plan_json.get("error"):
        return jsonify(trip_plan_json), 500

    final_response = trip_plan_json
    if "travel_dates_display" not in final_response or not final_response["travel_dates_display"]:
        final_response["travel_dates_display"] = weather_data_dict.get("travel_dates_display", f"{start_date_str} to {end_date_str}")
    if "destination_local_time_display" not in final_response or not final_response["destination_local_time_display"]:
        final_response["destination_local_time_display"] = weather_data_dict.get("destination_local_time_display", "N/A")
    if "destination_weather_summary" not in final_response or not final_response["destination_weather_summary"]:
        final_response["destination_weather_summary"] = weather_data_dict.get("weather_display", "Weather details unavailable.")

    return jsonify(final_response), 200