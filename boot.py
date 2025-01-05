import network
import ntptime
import time
import machine
import tft_config
import utime
import st7789
import gc
import sevensegment_20 as font20
import sevensegment_30 as font30
import sevensegment_40 as font40
import timesnewromanpsmt as font
import urequests
import json

# Load API key from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Weekday names (first three letters)
WEEKDAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
MONTHS = ["JAN", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
IMAGE_PATH = "src/images/"
API_KEY = config["api_key"]
LOC = config["loc"]
SSID = config["ssid"]
PASSWORD = config["password"]

API_URL = f"https://api.openweathermap.org/data/2.5/weather?q={LOC}&appid={API_KEY}&units=metric"
ICON_PATH = "src/images/{}_t.png"  # Local path to weather icons
LOGO = "hoot.png"

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to Wi-Fi network '{ssid}'...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print("Wi-Fi connected:", wlan.ifconfig())

def set_time_to_ist():
    try:
        # Sync with NTP
        ntptime.host = "pool.ntp.org"  # Set NTP server
        ntptime.settime()  # Sets RTC to UTC
        
        # Adjust to IST (UTC+5:30)
        utc_time = time.localtime()
        ist_offset_seconds = 5 * 3600 + 30 * 60
        ist_time = time.localtime(time.mktime(utc_time) + ist_offset_seconds)

        # Set the RTC to IST (optional, if required)
        machine.RTC().datetime((
            ist_time[0], ist_time[1], ist_time[2], ist_time[6],
            ist_time[3], ist_time[4], ist_time[5], 0
        ))
        print("Time synchronized to IST:", ist_time)
        return ist_time
    except Exception as e:
        print(f"Error setting time: {e}")
        
def fetch_weather_data():
    """Fetches weather data from the OpenWeatherMap API."""
    try:
        response = urequests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            weather_main = data["weather"][0]["main"]
            temp = data["main"]["temp"]
            temp_min = data["main"]["temp_min"]
            temp_max = data["main"]["temp_max"]
            icon = data["weather"][0]["icon"]
            sunrise = data["sys"]["sunrise"]
            sunset = data["sys"]["sunset"]
            loc = data["name"]
            return weather_main, temp, temp_min, temp_max, icon, sunrise, sunset, loc
        else:
            print(f"Failed to fetch weather data: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None
    
def display_weather_icon(tft, icon_id, x, y):
    """Displays the weather icon from the local path."""
    try:
        icon_path = ICON_PATH.format(icon_id)
        tft.png(icon_path, x, y,True)

    except Exception as e:
        print(f"Error displaying weather icon: {e}")
    
def main():
    try:
        gc.collect()

        # Initialize the display
        tft = tft_config.config(1)
        tft.init()

        time_color = st7789.WHITE
        background_color = st7789.BLACK
        weather_color = st7789.CYAN

        # Fetch initial weather data
        weather_data = fetch_weather_data()
        if weather_data:
            weather_main, temp, temp_min, temp_max, icon_id, sunrise, sunset, loc = weather_data
        else:
            weather_main, temp, temp_min, temp_max, icon_id, sunrise, sunset, loc = "N/A", "N/A", "N/A", "N/A", "01d", 0, 0,"N/A"

        # Variables to track last displayed time
        last_hour = None
        last_minute = None
        last_transition = None  # Tracks last sunrise/sunset event


        while True:

            # Get the current time
            current_time = time.time()
            year, month, date, hour, minute, second, weekday, _ = time.localtime()
            # Check if it's time to update weather data (at sunrise or sunset)
            if last_transition is None or (current_time >= sunrise and last_transition < sunrise) or (current_time >= sunset and last_transition < sunset):
                print("Updating weather data at sunrise/sunset...")
                weather_data = fetch_weather_data()
                if weather_data:
                    weather_main, temp, temp_min, temp_max, icon_id, sunrise, sunset, loc = weather_data
                    last_transition = max(sunrise, sunset)
            
            # Display the current weather and time
            display_weather_icon(tft, icon_id, 20, 50)  # Display icon at top-left

            # Format and display weather details
            weather_str = f"{weather_main}: {temp}°C"
            min_temp_range_str = f"Min: {temp_min}°C "
            max_temp_range_str = f"Max: {temp_max}°C"
            loc_str = f"Loc: {loc}"
            tft.write(font, weather_main, 15, 90, weather_color, st7789.BLACK)
            tft.write(font, min_temp_range_str, 200, 10, weather_color, st7789.BLACK)
            tft.write(font, max_temp_range_str, 200, 40, weather_color, st7789.BLACK)
            tft.write(font, loc_str, 200, 70, weather_color, st7789.BLACK)

            # Convert to 12-hour format
            period = "AM" if hour < 12 else "PM"
            hour_12 = hour % 12
            hour_12 = 12 if hour_12 == 0 else hour_12  # Handle midnight and noon

             # Check if the minute or hour has changed
            if hour != last_hour or minute != last_minute or second != last_second:
                # Format time and date
                day_str = WEEKDAYS[weekday]  # Get the day of the week
                time_str = "{:02d}:{:02d}:{:02d}".format(hour_12, minute, second)
                date_str = "{:02d} {}".format(date, MONTHS[month - 1])
                year_str = "{:04d}".format(year)
                period_str = "{}".format(period)

                # Calculate positions for time and date
                time_col = 30
                time_row = 40
                date_col = tft.width() // 2 - font.MAX_WIDTH * len(date_str) // 2
                date_row = time_row + font.HEIGHT + 10  # Space below the time

                # Display the updated time and date
                tft.write(font40, day_str, 10, 10, time_color, background_color)
                tft.write(font40, time_str, 10, 120, time_color, background_color)
                tft.write(font30, period_str, 145, 130, time_color, background_color)
                tft.write(font40, year_str, 100, 10, time_color, background_color)
                tft.write(font40, date_str, 80, 70, time_color, background_color)
                tft.png(LOGO, 240, 110,True)
                last_hour = hour
                last_minute = minute
                last_second = second

            time.sleep(0.1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up and deinitialize
        tft.deinit()
        gc.collect()

# Main Script
if __name__ == "__main__":

    connect_to_wifi(SSID, PASSWORD)
    ist_time = set_time_to_ist()
    main()

