from sense_hat import SenseHat  
import time  
import sys  
from ISStreamer.Streamer import Streamer  
  
# --------- User Settings ---------
CITY = "Munich"
BUCKET_NAME = ":partly_sunny: " + CITY + " Weather"
BUCKET_KEY = "sensehat"
ACCESS_KEY = "yHRoXJxikEPGyXluXc7muoagOCKhRGYo"
SENSOR_LOCATION_NAME = "Office"
MINUTES_BETWEEN_SENSEHAT_READS = 0.1
# ---------------------------------

streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
  
sense = SenseHat()  
  
while True:
  # Read the sensors
  temp_c = sense.get_temperature()
  humidity = sense.get_humidity() 
  pressure_mb = sense.get_pressure() 

  # Format the data
  temp_f = temp_c * 9.0 / 5.0 + 32.0
  temp_f = float("{0:.2f}".format(temp_f))
  humidity = float("{0:.2f}".format(humidity))
  pressure_in = 0.03937008*(pressure_mb)
  pressure_in = float("{0:.2f}".format(pressure_in))

  # Print and stream 
  print SENSOR_LOCATION_NAME + " Temperature(C): " + str(temp_c)
  print SENSOR_LOCATION_NAME + " Humidity(%): " + str(humidity)
  print SENSOR_LOCATION_NAME + " Pressure(mb): " + str(pressure_mb)
  streamer.log(":sunny: " + SENSOR_LOCATION_NAME + " Temperature(F)", temp_c)
  streamer.log(":sweat_drops: " + SENSOR_LOCATION_NAME + " Humidity(%)", humidity)
  streamer.log(":cloud: " + SENSOR_LOCATION_NAME + " Pressure(mb)", pressure_mb)

  streamer.flush()
  time.sleep(60*MINUTES_BETWEEN_SENSEHAT_READS)
