#!/usr/bin/python

import os
import urllib2
import json
import glob
from time import sleep,time,strftime
import RPi.GPIO as io
from ISStreamer.Streamer import Streamer
from sense_hat import SenseHat 

# --------- User Settings ---------
STATE = "Germany"
CITY = "Munich"
SENSOR_LOCATION_NAME = "Office"
WUNDERGROUND_API_KEY = "e71507fc5fe0780c"
BUCKET_NAME = ":partly_sunny: " + CITY + " Weather"
BUCKET_KEY = "wu1"
ACCESS_KEY = "yHRoXJxikEPGyXluXc7muoagOCKhRGYo"
MINUTES_BETWEEN_READS =10
METRIC_UNITS = True
# ---------------------------------

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def get_conditions():
        api_conditions_url = "http://api.wunderground.com/api/" + WUNDERGROUND_API_KEY + "/geolookup/conditions/forecast/q/" + STATE + "/" + CITY + ".json"
        try:
                f = urllib2.urlopen(api_conditions_url)
        except:
                return []
        json_conditions = f.read()
        f.close()
        return json.loads(json_conditions)

def get_astronomy():
        api_astronomy_url = "http://api.wunderground.com/api/" + WUNDERGROUND_API_KEY + "/geolookup/astronomy/forecast/q/" + STATE + "/" + CITY + ".json"
        try:
		f = urllib2.urlopen(api_astronomy_url)
	except:
		print "Failed to get astronomy"
		return []		
	json_astronomy = f.read()
	f.close()
	return json.loads(json_astronomy)

def is_night(astronomy):
	sunrise_hour = int(astronomy['moon_phase']['sunrise']['hour'])
	sunrise_min  = int(astronomy['moon_phase']['sunrise']['minute'])
	sunset_hour  = int(astronomy['moon_phase']['sunset']['hour'])
	sunset_min   = int(astronomy['moon_phase']['sunset']['minute'])
	current_hour = int(astronomy['moon_phase']['current_time']['hour'])
	current_min  = int(astronomy['moon_phase']['current_time']['minute'])
	if ( (current_hour < sunrise_hour) or
	     (current_hour > sunset_hour) or
	     ((current_hour == sunrise_hour) and
	      (current_min < sunrise_min)) or 
	     ((current_hour == sunset_hour) and
	      (current_min > sunset_min)) ):
		return True
	return False

def moon_icon(moon_phase):
	icon = {
		"New Moon"        : ":new_moon:",
		"Waxing Crescent" : ":waxing_crescent_moon:",
		"First Quarter"   : ":first_quarter_moon:",
		"Waxing Gibbous"  : ":waxing_gibbous_moon:",
		"Full Moon"       : ":full_moon:",
		"Full"            : ":full_moon:",
		"Waning Gibbous"  : ":waning_gibbous_moon:",
		"Last Quarter"    : ":last_quarter_moon:",
		"Waning Crescent" : ":waning_crescent_moon:",
	}
	return icon.get(moon_phase,":crescent_moon:")

def weather_icon(weather_conditions):
	icon = {
		"clear"            : ":sun_with_face:",
		"cloudy"           : ":cloud:",
		"flurries"         : ":snowflake:",
		"fog"              : ":foggy:",
		"hazy"             : ":foggy:",
		"mostlycloudy"     : ":cloud:",
		"mostlysunny"      : ":sun_with_face:",
		"partlycloudy"     : ":partly_sunny:",
		"partlysunny"      : ":partly_sunny:",
		"sleet"            : ":sweat_drops: :snowflake:",
		"rain"             : ":umbrella:",
		"snow"             : ":snowflake:",
		"sunny"            : ":sun_with_face:",
		"tstorms"          : ":zap: :umbrella:",
		"unknown"          : ":sun_with_face:",
	}
	return icon.get(weather_conditions,":sun_with_face:")

def weather_status_icon(conditions, astronomy):
	moon_phase = astronomy['moon_phase']['phaseofMoon']
	weather_conditions = conditions['current_observation']['icon']
	icon = weather_icon(weather_conditions)
	if is_night(astronomy):
		if ((icon == ":sunny:") or
		    (icon == ":partly_sunny:") or
		    (icon == ":sun_with_face:")):
			return moon_icon(moon_phase)
	return icon

def wind_dir_icon(conditions, astronomy):
	icon = {
		"East"     : ":arrow_right:",
		"ENE"      : ":arrow_upper_right:",
		"ESE"      : ":arrow_lower_right:",
		"NE"       : ":arrow_upper_right:",
		"NNE"      : ":arrow_upper_right:",
		"NNW"      : ":arrow_upper_left:",
		"North"    : ":arrow_up:",
		"NW"       : ":arrow_upper_left:",
		"SE"       : ":arrow_lower_right:",
		"South"    : ":arrow_down:",
		"SSE"      : ":arrow_lower_right:",
		"SSW"      : ":arrow_lower_left:",
		"SW"       : ":arrow_lower_left:",
		"Variable" : ":arrows_counterclockwise:",
		"West"     : ":arrow_left:",
		"WNW"      : ":arrow_upper_left:",
		"WSW"      : ":arrow_lower_left:",
	}
	return icon.get(conditions['current_observation']['wind_dir'],":crescent_moon:")	

# get CPU temperature
def get_cpu_temp():
  res = os.popen("vcgencmd measure_temp").readline()
  t = float(res.replace("temp=","").replace("'C\n",""))
  return(t)

# use moving average to smooth readings
def get_smooth(x):
  if not hasattr(get_smooth, "t"):
    get_smooth.t = [x,x,x]
  get_smooth.t[2] = get_smooth.t[1]
  get_smooth.t[1] = get_smooth.t[0]
  get_smooth.t[0] = x
  xs = (get_smooth.t[0]+get_smooth.t[1]+get_smooth.t[2])/3
  return(xs)

def main():
        sense = SenseHat()
        conditions = get_conditions()
        astronomy = get_astronomy()
        if ('current_observation' not in conditions) or ('moon_phase' not in astronomy):
                print "Error! Wunderground API call failed, check your STATE and CITY and make sure your Wunderground API key is valid"
                if 'error' in conditions['response']:
                        print "Error Type: " + conditions['response']['error']['type']
                        print "Error Description: " + conditions['response']['error']['description']
                exit()
#        else:
#                streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
 #               streamer.log(":house: Location",conditions['current_observation']['display_location']['full'])
        while True:
                # -------------- Sense Hat --------------
                # Read the sensors
            	t1 = sense.get_temperature_from_humidity()
		t2 = sense.get_temperature_from_pressure()
  		t_cpu = get_cpu_temp()
		humidity = sense.get_humidity()
                pressure_raw = sense.get_pressure()
 		
		# calculates the real temperature compesating CPU heating
  		t = (t1+t2)/2
  		t_corr = t - ((t_cpu-t)/1.5)
  		t_corr = get_smooth(t_corr)
		
		#correct pressure for altitude
		altitude = 520
		pressure_mb = pressure_raw/pow(1-(0.0065*altitude)/(t_corr+0.0065*altitude+273.15),5.255)
		####temp_c = sense.get_temperature()

                # Format the data
                temp_f = t_corr * 9.0 / 5.0 + 32.0
                temp_f = float("{0:.2f}".format(temp_f))
                temp_c = float("{0:.2f}".format(t_corr))
                humidity_ = float("{0:.2f}".format(humidity))
                pressure_in = 0.0295301*(pressure_mb)
                pressure_in = float("{0:.2f}".format(pressure_in))
                pressure_mb = float("{0:.2f}".format(pressure_mb))

		# Print and stream 
		if (METRIC_UNITS):
			print SENSOR_LOCATION_NAME + " Temperature(C): " + str(temp_c)
			print SENSOR_LOCATION_NAME + " Pressure(mb): " + str(pressure_mb)
#			streamer.log(":sunny: " + SENSOR_LOCATION_NAME + " Temperature(C)", temp_c)
#			streamer.log(":cloud: " + SENSOR_LOCATION_NAME + " Pressure (mb)", pressure_mb)
		else:
			print SENSOR_LOCATION_NAME + " Temperature(F): " + str(temp_f)
			print SENSOR_LOCATION_NAME + " Pressure(IN): " + str(pressure_in)
#			streamer.log(":sunny: " + SENSOR_LOCATION_NAME + " Temperature(F)", temp_f)
#			streamer.log(":cloud: " + SENSOR_LOCATION_NAME + " Pressure (IN)", pressure_in)
		print SENSOR_LOCATION_NAME + " Humidity(%): " + str(humidity_)
#		streamer.log(":sweat_drops: " + SENSOR_LOCATION_NAME + " Humidity(%)", humidity_)

		# -------------- Wunderground --------------
		conditions = get_conditions()
		astronomy = get_astronomy()

 		wtemp_c = -100.0
		wdewp_c = -100.0
		humidity = -100.0
		wpressure_mb = -100.0
		wwind = -100.0
		wwindgust = -100.0
		wwinddir = "NONE"
		wprecip_1hr_metric = -100.0
		wprecip_today_metric = -100.0
		wUV = -100.0

		if ('current_observation' not in conditions) or ('moon_phase' not in astronomy):
			print "Error! Wunderground API call failed. Skipping a reading then continuing ..."
		else:
			humidity_pct = conditions['current_observation']['relative_humidity']
			humidity = humidity_pct.replace("%","")

			# Stream valid conditions to Initial State
#			streamer.log(":cloud: " + CITY + " Weather Conditions",weather_status_icon(conditions, astronomy))
#			streamer.log(":crescent_moon: Moon Phase",moon_icon(astronomy['moon_phase']['phaseofMoon']))
#			streamer.log(":dash: " + CITY + " Wind Direction",wind_dir_icon(conditions, astronomy))
			wwinddir = conditions['current_observation']['wind_dir']
			if (METRIC_UNITS):
				if isFloat(conditions['current_observation']['temp_c']): 
					wtemp_c = conditions['current_observation']['temp_c']
#					streamer.log(CITY + " Temperature(C)",conditions['current_observation']['temp_c'])
				if isFloat(conditions['current_observation']['dewpoint_c']):
					wdewp_c = conditions['current_observation']['dewpoint_c']
#					streamer.log(CITY + " Dewpoint(C)",conditions['current_observation']['dewpoint_c'])
				if isFloat(conditions['current_observation']['wind_kph']):
                                        wwind = conditions['current_observation']['wind_kph']
#					streamer.log(":dash: " + CITY + " Wind Speed(KPH)",conditions['current_observation']['wind_kph'])
				if isFloat(conditions['current_observation']['wind_gust_kph']):
                                        wwindgust = conditions['current_observation']['wind_gust_kph']
#					streamer.log(":dash: " + CITY + " Wind Gust(KPH)",conditions['current_observation']['wind_gust_kph'])
				if isFloat(conditions['current_observation']['pressure_mb']):
                                        wpressure_mb = conditions['current_observation']['pressure_mb']
#					streamer.log(CITY + " Pressure(mb)",conditions['current_observation']['pressure_mb'])
				if isFloat(conditions['current_observation']['precip_1hr_metric']):
                                        wprecip_1hr_metric = conditions['current_observation']['precip_1hr_metric']
#					streamer.log(":umbrella: " + CITY + " Precip 1 Hour(mm)",conditions['current_observation']['precip_1hr_metric'])
				if isFloat(conditions['current_observation']['precip_today_metric']):
                                        wprecip_today_metric = conditions['current_observation']['precip_today_metric']
#					streamer.log(":umbrella: " + CITY + " Precip Today(mm)",conditions['current_observation']['precip_today_metric'])
#			else:
#				if isFloat(conditions['current_observation']['temp_f']): 
#					streamer.log(CITY + " Temperature(F)",conditions['current_observation']['temp_f'])
#				if isFloat(conditions['current_observation']['dewpoint_f']):
#					streamer.log(CITY + " Dewpoint(F)",conditions['current_observation']['dewpoint_f'])
#				if isFloat(conditions['current_observation']['wind_mph']):
#					streamer.log(":dash: " + CITY + " Wind Speed(MPH)",conditions['current_observation']['wind_mph'])
#				if isFloat(conditions['current_observation']['wind_gust_mph']):
#					streamer.log(":dash: " + CITY + " Wind Gust(MPH)",conditions['current_observation']['wind_gust_mph'])
#				if isFloat(conditions['current_observation']['pressure_in']):
#					streamer.log(CITY + " Pressure(IN)",conditions['current_observation']['pressure_in'])
#				if isFloat(conditions['current_observation']['precip_1hr_in']):
#					streamer.log(":umbrella: " + CITY + " Precip 1 Hour(IN)",conditions['current_observation']['precip_1hr_in'])
#				if isFloat(conditions['current_observation']['precip_today_in']):
#					streamer.log(":umbrella: " + CITY + " Precip Today(IN)",conditions['current_observation']['precip_today_in'])
			if isFloat(conditions['current_observation']['solarradiation']):
				wsolarradiation = conditions['current_observation']['solarradiation']
#				streamer.log(":sunny: " + CITY + " Solar Radiation (watt/m^2)",conditions['current_observation']['solarradiation'])
#			if isFloat(humidity):
#				streamer.log(":droplet: " + CITY + " Humidity(%)",humidity)
			if isFloat(conditions['current_observation']['UV']):
				wUV = conditions['current_observation']['UV']
#				streamer.log(":sunny: " + CITY + " UV Index:",conditions['current_observation']['UV'])
#			streamer.flush()
		with open("meteo_data.csv","a+") as log:
			log.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(strftime("%Y-%m-%d %H:%M:%S"),
												t1,
												t2,
												t_cpu,
												temp_c,
												pressure_mb,
												humidity_,
												wtemp_c,
												wdewp_c,
												humidity,
												wpressure_mb,
												wwind,
												wwindgust,
												wwinddir,
												wprecip_1hr_metric,
												wprecip_today_metric,
												wUV
											))	
#		time.sleep(60*MINUTES_BETWEEN_READS)
		break

if __name__ == "__main__":
    main()


