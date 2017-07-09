#! /usr/bin/python3


#Получает текущий IP адрес. Проверяет есть ли он в списке ip_list.
#Если таког IP нету, то добавляет его в список. Паралельно ведет лог.



import subprocess, time, re
import saulog

#Файл со списком IP
ip_list='/var/log/andrew/ip_list'
#Лог для записи сообщений
log='/var/log/andrew/ip_how_often.log'

# Получает текущий IP адресс. Возврашает его значение.
def getIP():

    ifconfig=subprocess.check_output('ifconfig',shell=True,
                                    universal_newlines=True)
    ppp=str(ifconfig)
    ppp=ppp.split('ppp0')
    ip_addr=re.search(r'(?<=inet addr:).+(?=\sP-t-P:)',str(ppp[1]))
    ip_addr=ip_addr.group(0)
    print('Текущий IP адресс - {0}'.format(ip_addr))
    return  ip_addr

# Считает количество IP в файле.
def countIpList():

    f1=open(ip_list)
    i=0
    for x in f1:
        i=i+1
    return i


ip_addr=getIP()
f1=open(ip_list,'r')

exist=False
for line in f1:
    if (re.search(ip_addr, line)) != None:
        exist=True
        break
f1.close()

if exist == False:

    f1=open(ip_list,'a')
    saulog.WriteLog(log,'Был добавлен следующий IP - {0}'.format(ip_addr))
    f1.write(ip_addr+'\n')
    f1.close()
    saulog.WriteLog(log,'Всего в списке: {0} - IP'.format(countIpList()))
else:
    saulog.WriteLog(log,'Этого IP - {0} - Уже есть в списке.'.format(ip_addr))

