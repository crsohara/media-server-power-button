#!/usr/bin/python3
import os # Gives Python access to Linux commands
from os.path import join, dirname
from dotenv import load_dotenv
import subprocess
import time # Proves time related commands
import RPi.GPIO as GPIO # Gives Python access to the GPIO pins
import requests
import logging
from logging.handlers import RotatingFileHandler

DIR = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
f_handler = RotatingFileHandler(join(DIR, 'button-py.log'), maxBytes=2000, backupCount=2)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(f_handler)

dotenv_path = join(DIR, '.env')
load_dotenv(dotenv_path)
IPV4 = os.getenv('IPV4')
MAC = os.getenv('MAC')


state = ''

# GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
# Set the GPIO pin naming mode
GPIO.setwarnings(False) # Suppress warnings

ButtonPin = 14
RedPin = 8
GreenPin = 7

GPIO.setup(RedPin, GPIO.OUT)
GPIO.output(RedPin, GPIO.LOW)
GPIO.setup(GreenPin, GPIO.OUT)
GPIO.setup(GreenPin, GPIO.LOW)
GPIO.setup(ButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def green():
  print('running green')
  GPIO.output(GreenPin, GPIO.HIGH)
  GPIO.output(RedPin, GPIO.LOW)

def red():
  print('running red')
  GPIO.output(GreenPin, GPIO.LOW)
  GPIO.output(RedPin, GPIO.HIGH)

def reset():
  print('running reset')
  GPIO.output(GreenPin, GPIO.LOW)
  GPIO.output(RedPin, GPIO.LOW)

def blink(argument):
  global state
  if state == argument:
    return

  state = argument

  print('running blink')
  switcher = {
    'fail': red,
    'success': green,
  }
  func = switcher.get(argument, lambda: reset())
  return func()

def run_wakeonlan():
  print("Button pressed, waking machine")
  process = subprocess.Popen(['wakeonlan', MAC], stdout=subprocess.PIPE, universal_newlines=True)
  stdout, stderr = process.communicate()
  print(stdout)
  print(stderr)

def run_shutdown():
  print("Long pressed, shutting down")
  try:
    print('Attempting to shut down...')
    r = requests.get('http://' + IPV4 + ':9979/shutdown')
    # print(r)
    # logger.info(r)
  except:
    print('ERROR: No route to host, machine already down?')

def button_press(channel):
  start_time = time.time()
  print('pressing button')

  while GPIO.input(channel) == 0:
    pass

  buttonTime = time.time() - start_time
  logger.info('buttonTime')
  logger.info(buttonTime)
  print(buttonTime)
  if buttonTime < 0.175:
    print('fluctuation, passing')
    logger.info('^ fluctuation, passing')

  if buttonTime >= 3:
    logger.info('running shutdown')
    run_shutdown()
  elif buttonTime >= 0.175:
    logger.info('running wake on lan')
    run_wakeonlan()


GPIO.add_event_detect(ButtonPin, GPIO.FALLING, callback=button_press, bouncetime=1000)

def status_ping():
  try:
      response = subprocess.check_output(
          ['ping', '-c', '1', IPV4],
          stderr=subprocess.STDOUT,  # get all output
          universal_newlines=True  # return string not bytes
      )
      return('success')
  except subprocess.CalledProcessError:
      response = None
      return('fail')

try:
  while True:
    blink(status_ping())
    time.sleep(1) # Sleep for 0.5 seconds
except KeyboardInterrupt:
  print('Exiting')
finally:
  GPIO.cleanup()
