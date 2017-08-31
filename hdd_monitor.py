#!/usr/bin/python3

#        отступы табуляцией
#        by Andrew Sotnikov aka Luca Brasi,
#        e-mail: andrew.sotnikov@zoho.com
#        --------------

#----------------------------ЗАВИСИМОСТИ----------------------------

#            sudo apt-get install python3-matplotlib

#-------------------------------------------------------------------

import saulog, subprocess,time, os, re
import matplotlib.pyplot as plt

os.putenv('DISPLAY',':0.0')
logfile='/var/log/andrew/hdd_temp'

# Проверить наличие файла. Если  нет то создать
try:
    f=open(logfile)
    f.close()

except FileNotFoundError:
    print('log\'а нету...')
    f=open(logfile,'a')
    f.write(time.strftime("%a, %d %b %Y")+'\n')
    f.close()

# Смотрим какой сегодня день. Если лог вчерашний - молча его затираем и создаем
# новый. Если лог сегодняшний продолжаем туда писать.

sameDay=False
f=open(logfile,'r')
for line in f:
    if line == (time.strftime("%a, %d %b %Y")+'\n'):
        sameDay=True
        print('Оу, да сегодня тоже число')
f.close()

if sameDay==False:
    os.remove(logfile)
    print('файл успешно удален :)')

# Процесс записи в лог
raw_output=subprocess.check_output('''/usr/sbin/hddtemp /dev/sda''',shell=True, universal_newlines=True)
pattern=r'.{2}(?=..$)'
res=re.search(pattern,raw_output)
res=res.group(0)
print('Текущая температура {0}'.format(res))

#Открытие файла на чтение. Сверим последнюю строку лога. Если текущая 
#температураотличаеться - пишем ее значение в лог. В противном случае идем мимо
f=open(logfile,'r')
for line in f:
    lastLine=line
f.close()

if (re.search(res, lastLine)) == None:
    f = open(logfile, 'a')
    f.write('{0};{1};{2}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S'), 
                                   round(time.time()),res[:2]))
    f.close()
    print("Ничего подобного, запишем инфу в лог")

class DrawPlot():

    logfile='/var/log/andrew/hdd_temp'

    def __init__(self):

        self.parseLog()
        self.doHumanTimeVal()
        self.calcTimeForAxis()
        self.doPlot()
        

    def doPlot(self):
        
        print('Запускаем plot')
        my_xticks = self.axis_points
        plt.xticks(self.x, my_xticks)
        print('Создали оси')
        plt.plot(self.x, self.y)
        plt.xlabel('Time')
        plt.ylabel('Deegrees by celsium')
        print('График должен быть нарисован')
        plt.savefig('/var/log/andrew/temperature.png')

    def parseLog(self):

        i=0
        x=[];y=[];labels=[]
        f=open(logfile,'r')
        for line in f:

            if (i != 0):
                temp_str=line.split(';')
#                Добавляем labels
                labels.append(temp_str[0])
#                Добавляем время, расположение будет на оси x
                x.append(temp_str[1])
#                Добавляем температуру, расположение будет на оси y
                y.append(temp_str[2][:2])

            i=i+1
        self.x=x
        self.y=y

#    С целью лучшего отображения значений времени на графике они будут 
#    не в формате time.time(), а в минутах
    def doHumanTimeVal(self):

#        Начальная точка времени
        start_time=int(self.x[0])
        new_x=[]
        
#        Получим время в минутах да и сразу перезапишем его
        for x in self.x:
            x=int(x)
#            Сузим интервал времени для большей удобочитаемости
            time_x_in_mins=round((x-start_time))
            new_x.append(time_x_in_mins)
        self.gmt_values=self.x
        self.x=new_x
        print(self.x)
        print(self.y)
        

#    Получим значения для оси. Берем крайние значения time.time() и получаем 
#    промежуточные значения для оси.
    def calcTimeForAxis(self):

#        Количество интервалов между наибольшим и наименьшим значением
        intervals=len(self.gmt_values)-1
#        Начальное значение оси
        begin=int(self.gmt_values[0])

        lastInd=len(self.gmt_values)-1
#        Конечное значение оси
        end=int(self.gmt_values[lastInd])
#        Сделаем список значений для x-овой оси
        self.gmt_points=[]
#        Пишем начало
        self.gmt_points.append(begin)

#        Получим смещение для высчитывания промежуточных точек
        offset=round((end-begin)/intervals)
        new_val=begin
#        Пишем промежуточные точки
        for x in range(intervals):
            new_val=new_val+offset
            self.gmt_points.append(new_val)

        print(self.gmt_points)


#        Преобразуем сырые значения gmt_points в человеческий формат
        self.axis_points=[]
        for gmt_point in self.gmt_points:

            human_val=time.strftime('%H:%M',time.localtime(gmt_point))
            self.axis_points.append(human_val)

        print('Вот полный список временных отметок на оси {0}'.format(self.axis_points))



pl=DrawPlot()



