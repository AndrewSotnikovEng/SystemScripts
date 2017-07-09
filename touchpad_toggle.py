#!/bin/python3

#Скрипт для вкл/выкл тачпада. Легко поддается bind'у на кнопку.
#Предварительно желательно проверить эффект от synclient TouchpadOff=1
#by Luca Brasi

import subprocess

state = subprocess.check_output("synclient -l | grep Touch",shell=True, universal_newlines=True)
state = state.strip()
print (state)

if (state == "TouchpadOff             = 0"):
	subprocess.call("/usr/bin/synclient TouchpadOff=1", shell=True)
	print('Отлючили')
else:
	subprocess.call("/usr/bin/synclient TouchpadOff=0", shell=True)
	print('Включили')
