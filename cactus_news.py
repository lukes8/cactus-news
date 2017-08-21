#!/usr/bin/python
# -*- coding: utf-8 -*- 

import urllib
import sys
import os.path
import RPi.GPIO as GPIO
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config

log_count = 0
cactus_tmp = "/home/pi/cactus_tmp"
Buzzer = 11    # pin11

# Functions
def findindex( str, str_find, index_from ):
  state = 0
  if len(str) == 0 or len(str_find) == 0 or index_from >= len(str):    
    print "log"
    sys.exit()
  res = str.find(str_find, index_from)
  if res == -1:
    print "log"
    sys.exit() 
  return res;
  
def setup(pin):
	global BuzzerPin
	BuzzerPin = pin
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(BuzzerPin, GPIO.OUT)
	GPIO.output(BuzzerPin, GPIO.HIGH)

def on():
	GPIO.output(BuzzerPin, GPIO.LOW)

def off():
	GPIO.output(BuzzerPin, GPIO.HIGH)

def beep(x):
	on()
	time.sleep(x)
	off()
	time.sleep(x)  

def destroy():
	GPIO.output(BuzzerPin, GPIO.HIGH)
	GPIO.cleanup()                     # Release resource
  
def send_email(fromaddr, frompwd, recipient, subject, body, verbose = False):
  """Send an email.
  """
  
  toaddr = recipient
  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = toaddr
  msg['Subject'] = subject
  msg.attach(MIMEText(body, 'plain', 'utf-8'))
  server = smtplib.SMTP('smtp.seznam.cz', 25)
  server.ehlo
  server.starttls()
  server.login(fromaddr, frompwd)
  text = msg.as_string()
  server.sendmail(fromaddr, toaddr, text)
  server.quit()

  if verbose:
    print "This mail has been sent:\n"
    print fromaddr
    print toaddr
    print 'Subject: %s\n' %subject
    print body   

def send_email_multiple(fromaddr, frompwd, recipients, subject, body, verbose = False):
  """Send the same email to more recipients.
  """
  for recipient in recipients:
    send_email(fromaddr, frompwd, recipient, subject, body, verbose)  

          
# Main program start from here  
setup(Buzzer)
destroy()

url = "https://www.mujkaktus.cz/homepage"
response = urllib.urlopen(url).read()

if len(response) == 0:
  sys.exit()

str_find = "květináče"
res = findindex(response, str_find, 0)
str_find2 = "<p>"
res2 = findindex(response, str_find2, res)
str_find3 = "</p>"
res3 = findindex(response, str_find3, res2)

str_message = response[res2:res3].lstrip('<p>').rstrip('</p>').strip()
if len(str_message) == 0:
  sys.exit()

is_new_message = True
if os.path.isfile(cactus_tmp):
  f = open(cactus_tmp, 'r')
  file_content = f.read()
  if file_content == str_message:
    is_new_message = False     

if is_new_message:
  print "Message: ", str_message
  fromaddr = config.login['email']
  frompwd = config.login['password']
  recipients = config.mailList
  send_email_multiple(fromaddr, frompwd, recipients, 'Zpráva od MůjKaktus', 'MůjKaktus:\n' + str_message, True)
  
  setup(Buzzer)
  beep(0.1)
  destroy()
  f = open(cactus_tmp, 'w')
  f.write(str_message)
  f.close()
else:
#   print "Older message...", str_message  
  sys.exit()  
  
