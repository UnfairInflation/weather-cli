# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Show the current weather for a city, with a little ASCII art icon.

Usage:
    uv run weather.py Copenhagen
    uv run weather.py "New York"
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Each icon is a list of 5 strings (lines), all padded to the same width
# so the text printed next to them lines up neatly.
ICONS = {
    "sun": [
        "    \\   /    ",
        "     .-.     ",
        "  - (   ) -  ",
        "     `-'     ",
        "    /   \\    ",
    ],
    "cloud": [
        "             ",
        "     .--.    ",
        "  .-(    ).  ",
        " (___.__)__) ",
        "             ",
    ],
    "rain": [
        "     .-.     ",
        "    (   ).   ",
        "   (___(__)  ",
        "    ' ' ' '  ",
        "   ' ' ' '   ",
    ],
    "snow": [
        "     .-.     ",
        "    (   ).   ",
        "   (___(__)  ",
        "    *  *  *  ",
        "   *  *  *   ",
    ],
    "fog": [
        "             ",
        " _ - _ - _ - ",
        "  _ - _ - _  ",
        " _ - _ - _ - ",
        "             ",
    ],
    "thunder": [
        "     .-.     ",
        "    (   ).   ",
        "   (___(__)  ",
        "     /_ /_   ",
        "      /  /   ",
    ],
}

# Open-Meteo reports conditions as WMO weather codes (numbers).
# This maps each code to a human-readable description and one of our icons.
WEATHER_CODES = {
    0: ("Clear sky", "sun"),
    1: ("Mainly clear", "sun"),
    2: ("Partly cloudy", "cloud"),
    3: ("Overcast", "cloud"),
    45: ("Fog", "fog"),
    48: ("Depositing rime fog", "fog"),
    51: ("Light drizzle", "rain"),
    53: ("Moderate drizzle", "rain"),
    55: ("Dense drizzle", "rain"),
    56: ("Light freezing drizzle", "rain"),
    57: ("Dense freezing drizzle", "rain"),
    61: ("Slight rain", "rain"),
    63: ("Moderate rain", "rain"),
    65: ("Heavy rain", "rain"),
    66: ("Light freezing rain", "rain"),
    67: ("Heavy freezing rain", "rain"),
    71: ("Slight snowfall", "snow"),
    73: ("Moderate snowfall", "snow"),
    75: ("Heavy snowfall", "snow"),
    77: ("Snow grains", "snow"),
    80: ("Slight rain showers", "rain"),
    81: ("Moderate rain showers", "rain"),
    82: ("Violent rain showers", "rain"),
    85: ("Slight snow showers", "snow"),
    86: ("Heavy snow showers", "snow"),
    95: ("Thunderstorm", "thunder"),
    96: ("Thunderstorm with slight hail", "thunder"),
    99: ("Thunderstorm with heavy hail", "thunder"),
}

COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def get_json(url: str, params: dict) -> dict:
    """Send a GET request with query parameters and return the parsed JSON."""
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(full_url, timeout=10) as response:
        return json.load(response)


def find_city(name: str) -> dict | None:
    """Look up a city by name. Returns the best match, or None if not found."""
    data = get_json(GEOCODING_URL, {"name": name, "count": 1, "language": "en"})
    results = data.get("results")  # key is missing entirely when nothing matches
    return results[0] if results else None


def get_current_weather(latitude: float, longitude: float) -> dict:
    """Fetch the current weather for a pair of coordinates."""
    data = get_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m,wind_direction_10m,weather_code",
            "wind_speed_unit": "ms",
        },
    )
    return data["current"]


def degrees_to_compass(degrees: float) -> str:
    """Turn a wind direction like 225° into a compass point like 'SW'."""
    index = round(degrees / 45) % 8
    return COMPASS[index]


def main() -> None:
    # sys.argv is the list of command-line words: ["weather.py", "New", "York"]
    if len(sys.argv) < 2:
        print("Usage: uv run weather.py <city name>")
        sys.exit(1)
    city_name = " ".join(sys.argv[1:])

    try:
        city = find_city(city_name)
        if city is None:
            print(f"Could not find a city called {city_name!r}.")
            sys.exit(1)
        weather = get_current_weather(city["latitude"], city["longitude"])
    except urllib.error.URLError as error:
        print(f"Network error: {error.reason}")
        sys.exit(1)

    code = weather["weather_code"]
    description, icon_name = WEATHER_CODES.get(code, (f"Unknown (code {code})", "cloud"))
    icon = ICONS[icon_name]

    # Build the place name, skipping parts that are missing (e.g. no region).
    place = ", ".join(
        part for part in (city["name"], city.get("admin1"), city.get("country")) if part
    )
    wind_dir = degrees_to_compass(weather["wind_direction_10m"])

    text_lines = [
        place,
        description,
        f"Temperature: {weather['temperature_2m']:.1f} °C",
        f"Wind:        {weather['wind_speed_10m']:.1f} m/s from {wind_dir}",
        "",
    ]

    # zip() pairs each icon line with a text line so we can print them side by side.
    print()
    for icon_line, text_line in zip(icon, text_lines):
        print(f"{icon_line}  {text_line}")


# This block only runs when the file is executed directly,
# not when it's imported by another Python file.
if __name__ == "__main__":
    main()
