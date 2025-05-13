
import json

def get_offline_response(place):
    try:
        with open("places.json", "r") as f:
            data = json.load(f)
        place_info = data.get(place.lower())
        if place_info:
            return f"Place: {place}\nBest Time: {place_info['best_time']}\nFamous Food: {place_info['food']}\nActivities: {place_info['activities']}\nRating: {place_info['rating']}\nReview: {place_info['review']}"
        else:
            return "Information not available for this place."
    except:
        return "Error loading offline data."
