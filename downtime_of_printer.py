#!/usr/bin/python3

#        отступы пробелами
#        by Andrew Sotnikov aka Luca Brasi,
#        e-mail: andrew.sotnikov@zoho.com
#        --------------
#        Определяет дефолтный принтер и смотрит сколко дней прошло
#        с последнего момента печати. Если больше 4ех дней посылает
#        окошко warnings, больше 7ми - critical.

import os,re, time, sys
from subprocess import *
from PyQt4 import QtGui, QtCore

# Открывает исходный файл и возващает его в реверсированном порядке.
# Принимает аргументы: filename - путь к файлу, replace=True - заменит
# исходный файл на реверсированный.

#     ################  ВАЖНО!  ##############
#    Если при выводе:    
#        lpstat -W completed
#    сначала последняя печать идет в начале, удали строку 32 ( ls=ls.reverse()).
#    Если последний сеанс печати в конце - ничего не трогай.

class ReverseFile:
    def __init__(self,filename,replace=False):
        self.doJobList()
        f1=open(filename)
        f2=open(filename+'_tmp','w')
        ls=[]
#        for x in f1:
#            ls.append(x)
        ls=reversed(ls)
        for x in ls:
            f2.write(x)

        f1.close()
        f2.close()
        if replace==True:
            os.remove(filename)
            os.rename((filename+'_tmp'),filename)

    def doJobList(self):
        os.chdir('/tmp/')
        call('lpstat -W completed > 12561', shell=True)

class getInfo():

    year={'Янв':31,'Фев':29,'Мар':31,
          'Апр':30,'Май':31,'чер':30,
          'Июл':31,'Авг':31,'Сен':30,
          'Окт':31,'Ноя':30,'Дек':31}

    month=('Янв','Фев','Мар','Апр','Май','чер',
           'Июл','Авг','Сен','Окт','Ноя','Дек')

    # Вызывает lpstat -d и парсит вывод.
    # Возвращает дефолтный имя дефолтного принтера.
    def getDefPrinter(self):
        pattern=check_output(['lpstat -d'],shell=True);pattern=str(pattern)
        res=re.search(r'(?<=:\s).+?(?=\\n)',pattern)
        printer=res.group(0)
        print('Твой дефолтный принтер - {0}'.format(printer))
        return printer


    def getPrLastDate(self):
        printer=self.getDefPrinter()
        f2=open('/tmp/12561')
        for x in f2:
            if (re.search(printer,x)) != None:
                print(x)
                break
        date=self.parseDate(x)
        self.getDifference(date)

        f2.close()

    # Получает строку формата:
    # Canon_E464-114 andrew  18432 Пнд 01 Фев 2016 21:06:54
    # Парсит string и возврщает список date, такого формата:
    # ('01', 'Фев', '2016')

    def parseDate(self,string):
        # date=re.search(r'.{11}\s(?=\d{2}:\d{2}:\d{2})',string)
        date=re.search(r'.(\d{2})\s(.{3})\s(\d{4})\s(?=\d{2}:\d{2}:\d{2})',
                       string)
        date=date.group(1,2,3)
        print(date)
        return date

    # Получает количество дней с момента последнего запуска принтера и
    # возвращает это значение.
    def getDifference(self,date):

        # Начало получения количества дней с момента последнего запуска
        d_from_last=0
        for x in self.month:
            if date[1] in x:
                d_from_last=d_from_last+int(date[0])
                break
            d_from_last=d_from_last+self.year[x]
        # Конец получения количества дней с момента последнего запуска

        doy=int(time.strftime('%j',time.gmtime()))
        year=int(time.strftime('%Y',time.gmtime()))
        if (int(date[2])) != year:
            doy=doy+365
        days_difference=doy-d_from_last
        print('Печать не проводилась {0} дней'.format(days_difference))
        self.days=days_difference

        # Окошко warnings
class DrawWarning(QtGui.QWidget):
    def __init__(self,days, parent=None,):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(960, 540, 300, 150)
        self.setWindowTitle('printer')
        font=QtGui.QFont()
        font.setPointSize(14)
        self.setFont(font)

        button_ok=QtGui.QPushButton('OK',self)

        button_ok.setFixedSize(100,40)
        self.connect(button_ok,QtCore.SIGNAL('clicked()'),QtGui.qApp,
                     QtCore.SLOT('quit()'))
        label=QtGui.QLabel('You don\'t print for a {0} '
              'days'.format(days))
        label2=QtGui.QLabel()
        pixmap=QtGui.QPixmap('/usr/share/icons/gnome/48x48/status/'
                         'messagebox_warning.png')
        label2.setPixmap(pixmap)

        grid=QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.setVerticalSpacing(20)
        grid.addWidget(label2,0,0,QtCore.Qt.AlignHCenter)
        grid.addWidget(label,1,0,QtCore.Qt.AlignHCenter)
        grid.addWidget(button_ok,2,0,1,1,QtCore.Qt.AlignHCenter)
        self.setLayout(grid)
        self.center()

        # Центрирует окно
    def center(self):

        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-
        size.height())/2)

        # Окошко critical
class DrawCritical(DrawWarning):

    def __init__(self,days, parent=None,):
        QtGui.QWidget.__init__(self, parent)

        self.setGeometry(960, 540, 300, 150)
        self.setWindowTitle('printer')
        font=QtGui.QFont()
        font.setPointSize(14)
        self.setFont(font)

        button_ok=QtGui.QPushButton('OK',self)

        button_ok.setFixedSize(100,40)
        self.connect(button_ok,QtCore.SIGNAL('clicked()'),QtGui.qApp,
                     QtCore.SLOT('quit()'))
        label=QtGui.QLabel('You don\'t print for a {0} '
              'days.\n       Do it immediately!'.format(days))
        label2=QtGui.QLabel()
        pixmap=QtGui.QPixmap('/usr/share/icons/gnome/48x48/status/'
                         'messagebox_critical.png')
        label2.setPixmap(pixmap)

        grid=QtGui.QGridLayout()
        grid.setSpacing(10)
        grid.setVerticalSpacing(20)
        grid.addWidget(label2,0,0,QtCore.Qt.AlignHCenter)
        grid.addWidget(label,1,0,QtCore.Qt.AlignHCenter)
        grid.addWidget(button_ok,2,0,1,1,QtCore.Qt.AlignHCenter)
        self.setLayout(grid)
        self.center()


if __name__ == "__main__":

    a=ReverseFile('/tmp/12561',replace=True)
    b=getInfo()
    b.getPrLastDate()
    days=b.days

    app = QtGui.QApplication(sys.argv)
    if days >=3 and days <7:
        qb = DrawWarning(days)
    elif days >= 7:
        qb = DrawCritical(days)
    try:
        qb.show()
        sys.exit(app.exec_())
    except Exception:
        pass
