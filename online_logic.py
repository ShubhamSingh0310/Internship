
import wikipedia

def get_online_response(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except:
        return "No information found online."
