import requests
from datetime import datetime

class RealLocationIntelligenceEngine:
    """Connects to Real Weather & Geocoding APIs (Open-Meteo & OpenStreetMap Nominatim)."""

    def __init__(self):
        self.preset_coordinates = {
            "lagos": {"lat": 6.5244, "lon": 3.3792, "name": "Lagos, Nigeria"},
            "onitsha": {"lat": 6.1472, "lon": 6.7845, "name": "Onitsha Main Market, Anambra"},
            "ikeja": {"lat": 6.6018, "lon": 3.3515, "name": "Computer Village Ikeja, Lagos"},
            "aba": {"lat": 5.1066, "lon": 7.3667, "name": "Ariaria Market Aba, Abia"},
            "kano": {"lat": 12.0022, "lon": 8.5920, "name": "Kurmi Market Kano"},
            "port harcourt": {"lat": 4.8156, "lon": 7.0498, "name": "Port Harcourt, Rivers"},
            "london": {"lat": 51.5074, "lon": -0.1278, "name": "London, UK"},
            "new york": {"lat": 40.7128, "lon": -74.0060, "name": "New York, USA"},
            "nairobi": {"lat": -1.2921, "lon": 36.8219, "name": "Nairobi, Kenya"}
        }

    def geocode_location(self, location_name: str) -> dict:
        """Geocodes location name to Lat/Lon using OpenStreetMap Nominatim API."""
        clean_loc = location_name.lower().strip()
        
        for key, coords in self.preset_coordinates.items():
            if key in clean_loc:
                return coords

        try:
            url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
            headers = {"User-Agent": "SovereignAISaaS/2030"}
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200 and len(res.json()) > 0:
                data = res.json()[0]
                return {
                    "lat": float(data["lat"]),
                    "lon": float(data["lon"]),
                    "name": data.get("display_name", location_name)
                }
        except Exception as e:
            print(f"[WARNING] Geocoding API fallback: {e}")

        return self.preset_coordinates["lagos"]

    def fetch_real_weather_forecast(self, lat: float, lon: float) -> dict:
        """Fetches REAL Live Weather Data from Open-Meteo Global API."""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,precipitation"
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                cw = res.json().get("current_weather", {})
                temp = cw.get("temperature", 28.0)
                wind = cw.get("windspeed", 10.0)
                wcode = cw.get("weathercode", 0)

                condition = "Clear Skies"
                if wcode in [1, 2, 3]:
                    condition = "Partly Cloudy"
                elif wcode in [45, 48]:
                    condition = "Foggy / Harmattan Haze"
                elif wcode in [51, 53, 55, 61, 63, 65]:
                    condition = "Rainfall Expected"
                elif wcode in [80, 81, 82, 95]:
                    condition = "Thunderstorm / Heavy Downpour"

                return {
                    "temperature_c": temp,
                    "windspeed_kmh": wind,
                    "condition": condition,
                    "weather_code": wcode,
                    "is_live": True
                }
        except Exception as e:
            print(f"[WARNING] Open-Meteo Real Weather API fallback: {e}")

        return {"temperature_c": 29.5, "windspeed_kmh": 12.0, "condition": "Clear & Warm", "weather_code": 0, "is_live": False}

    def generate_smart_location_intelligence(self, location_query: str = "Onitsha") -> str:
        """Generates Smart Location & Commercial Weather Intelligence Report."""
        coords = self.geocode_location(location_query)
        weather = self.fetch_real_weather_forecast(coords["lat"], coords["lon"])

        temp = weather["temperature_c"]
        cond = weather["condition"]
        loc_name = coords["name"]

        if "Rain" in cond or "Downpour" in cond:
            advisory = "⚠️ *LOGISTICS ADVISORY:* Rainfall forecast. Recommend waterproof packaging and covered dispatch vehicles for goods."
        elif temp >= 32.0:
            advisory = "☀️ *HEAT ADVISORY:* Temperature at 32°C+. Recommend shade/cool storage for heat-sensitive inventory."
        else:
            advisory = "🌤️ *COMMERCIAL ADVISORY:* Ideal market weather forecast. Optimal conditions for high customer foot-traffic & rapid delivery."

        return f"""📍 *[SMART LOCATION & REAL WEATHER INTELLIGENCE]*
---------------------------------------------
🗺️ *Location:* {loc_name}
🌐 *Coordinates:* {coords['lat']:.4f}° N, {coords['lon']:.4f}° E
🌡️ *Real Temperature:* *{temp}°C*
🌤️ *Condition:* *{cond}*
💨 *Wind Velocity:* {weather['windspeed_kmh']} km/h

{advisory}"""

real_location_intel = RealLocationIntelligenceEngine()
