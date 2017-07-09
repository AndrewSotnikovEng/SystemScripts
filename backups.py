#!/usr/bin/python3
#coding=utf8
#Этот скрипт умело делает бэкапы файлов

#На одном файловом уровне со скриптом нужно сделать файл .inner_data
#Формат файла следующий, имя_бэкапа, путь_к_элменту, имя_элемента, путь_кудаложить. Например:
#"gedit /usr/bin/ gedit ~/backup/"  gedit будет положен в паку backup и сохранен под именем gedit
#Также это дело пишеться в лог my_log

import time, saulog, os
import subprocess

#Адрес куда хотелось бы писать лог
log="/var/log/andrew/my_backup.log"

f=open('/media/Maindata/Дело/das_code/py/sys_scripts/.inner_data')

#Создать папку
def mkMonthDir():

    global full_path

    folder_name=time.strftime('%m_%B')
    #Путь с учетом папки месяца
    full_path=path_afterMove[:-1]+folder_name
    print(full_path)
    #Проверяем наличие пути
    if (os.path.exists(full_path)) == True:
        print('Уже есть такой путь {0}! Ничего не нужно '
              'делать'.format(full_path))

    else:
        os.mkdir(full_path)

        print('путь создан!')


for string in f.readlines():
    spl_str=string.split(' ')
#   Имя зип файла
    zipname="{0}_{1}.tar.bz2".format(time.strftime("%d"), spl_str[0])
#   Путь к источнику
    path_source = spl_str[1]
#   Путь куда переместить
    path_afterMove = spl_str[3]

    mkMonthDir()


    subprocess.call("tar -C "+path_source+ " -cvj -f"+ zipname +" "+ spl_str[2], shell=True)
    res=subprocess.call("mv {0} {1}".format(zipname,full_path), shell=True)

    if res == 0:
        message='Была сделана резервная копия файла {0}' \
                '___{1}'.format(path_source,spl_str[2])
        saulog.WriteLog(log,message)


f.close()    




