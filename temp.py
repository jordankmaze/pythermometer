import requests

class Thermometer:
    # define some intial variables 
    def __init__(self, api_url):
        self.api_url = api_url
        self.thresholds = {}
        self.last_reported_temperature= None

    # get a raw data temp from the api
    def get_temperature(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            temperature = response.json()['current']['temp_c']
            return temperature
        except requests.exceptions.RequestException as e:
            print(f"Error reading temp: {e}")
            return None

    # get a specific temperature measure in celsius
    def get_temperature_celsius(self):
        temperature = self.get_temperature()
        if temperature is not None:
            return round(temperature)
        return None
    
    # get a specific temperature measure in fahrenheit
    def get_temperature_fahrenheit(self):
        temperature_celsius = self.get_temperature_celsius()
        if temperature_celsius is not None:
            return round(temperature_celsius * 9/5 +32)
        return None

    # check if the value is going up or down
    def is_threshold_reached(self, current_temp, previous_temp, direction):
        if direction == 'up':
            return current_temp >= previous_temp
        elif direction == 'down':
            return current_temp <= previous_temp
        else:
            raise ValueError('Invalid direction value')

    # specify your threshold values
    def add_threshold(self, name, threshold_temp, callback, direction, measure):
        self.thresholds[name] = {
            'threshold_temp': threshold_temp,
            'callback': callback,
            'notified': False,
            'direction': direction,
            'measure': measure,
        }

    # check if the values you specified are being met
    def check_threshold(self, measure):
        if measure == 'C':
            current_temp = self.get_temperature_celsius()
        if measure == 'F':
            current_temp = self.get_temperature_fahrenheit()

        previous_temp = current_temp

        if current_temp is not None:
            for name, threshold in self.thresholds.items():
                threshold_temp = threshold['threshold_temp']
                callback = threshold['callback']
                notified = threshold['notified']
                direction = threshold['direction']

                is_reached = self.is_threshold_reached(current_temp, previous_temp, direction)

                if not notified and current_temp >= threshold_temp and is_reached:
                    callback(current_temp)
                    threshold['notified'] = True
                elif notified and current_temp < threshold_temp and is_reached:
                    threshold['notified'] = False

# callback function to notify you if values are met
def temp_callback(temp):
    print(f"Freezing point reached: {temp} C")

# create a thermometer object for reading the temperature from an external API
thermometer = Thermometer('http://api.weatherapi.com/v1/current.json?key=YOUR_API_KEY_GOES_HERE&q=Portland&aqi=no')

# examples of how to run
thermometer.add_threshold("freezing", 32, temp_callback, 'up', 'F')
    # thermometer.add_threshold("boiling", 100, temp_callback, 'down', 'C')

import time
while True:
    thermometer.check_threshold('F')
    time.sleep(5)
