import os
import requests
from dotenv import load_dotenv
from .base_tool import BaseTool

class Weather(BaseTool):
    def __init__(self):
        load_dotenv()
        super().__init__(
            name="weather",
            description="Fetches weather information for a given city. Input is only the name of the city. e.g. 'London'."
        )
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def use(self, query):
        """Fetches weather data for a given city"""
        if not query:
            raise ValueError("City cannot be empty.")

        url = f"{self.base_url}?q={query}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']

            return (
                f"The temperature in {query} is {temperature}°C. "
                f"The weather is {description}. "
                f"The humidity is {humidity}%. "
                f"The wind speed is {wind_speed} m/s."
            )
        
        return f"Failed to fetch weather data for {query}."



### For testing running directly the script
if __name__ == '__main__':
    weather = Weather()
    city = "Buenos Aires"

    result = weather.use(city)
    print(result)
