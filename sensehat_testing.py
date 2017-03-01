import os
import time
from sense_hat import SenseHat

def get_cpu_temp():
  res = os.popen("vcgencmd measure_temp").readline()
  t = float(res.replace("temp=","").replace("'C\n",""))
  return(t)


sense = SenseHat()

while True:
  t = sense.get_temperature_from_humidity()
  t_cpu = get_cpu_temp()
  h = sense.get_humidity()
  p = sense.get_pressure()

  # calculates the real temperature compesating CPU heating
  t_corr = t - ((t_cpu-t)/1.5)
  
  print("t=%.1f  t_cpu=%.1f  t_corr=%.1f  h=%d  p=%d" % (t, t_cpu, t_corr, round(h), round(p)))
  
  time.sleep(5)
