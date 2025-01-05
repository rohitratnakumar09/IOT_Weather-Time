# IOT_Weather and Time Display 

An ESP32-based IoT project that displays real-time weather and time information on an LCD screen.

📖 Description
IOT_Weather-Time is a smart IoT system that combines weather data and time synchronization to provide an elegant real-time display. Using the ESP32 microcontroller, it fetches weather updates from the OpenWeatherMap API and displays them alongside time and date on a TFT LCD. The project adapts dynamically for day and night modes, with weather icons and optimized API calls.

✨ Features
Real-Time Weather Updates: Displays current temperature, min/max temperatures, and weather conditions.
Day and Night Mode: Switches between day and night icons based on sunrise/sunset.
Time Synchronization: Automatically syncs to Indian Standard Time (UTC+5:30) via NTP.
Optimized API Calls: Updates weather data only during sunrise and sunset.

📸 Project Preview

Sample display for day mode.

![Alt text](20250105_091002.jpg)

🌐 API Used
This project uses the OpenWeatherMap API to fetch real-time weather data.

📚 References
This project was inspired by and built upon the following resources:
OpenWeatherMap API Guide

A helpful guide on using OpenWeatherMap API with Python and ESP32.
ST7789 Display Library >> https://github.com/russhughes/st7789s3_mpy

OpenWeatherMap Icons >> https://github.com/rodrigokamada/openweathermap

