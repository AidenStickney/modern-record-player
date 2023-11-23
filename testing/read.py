#!/usr/bin/env python

import RPi.GPIO as GPIO
import sys
sys.path.append('/home/aidenstickney/MFRC522-python')
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
        print("Waiting for you to scan an RFID sticker/card")
        id = reader.read()[0]
        print("The ID for this card is:", id)
        
finally:
        GPIO.cleanup()
        
