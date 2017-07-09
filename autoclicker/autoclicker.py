#! /usr/bin/python

#        Данный код посвящаеться автокликеру.
#        отступы табуляцией
#        by Luca Brasi, e-mail: andrew.sotnikov@zoho.com
#        --------------
#         Кнопки для имитации кликов:
#         L_Crtl - ЛКМ, L_Alt  - дабл клик, L_Shift - ПКМ 


import pyautogui, time, pyxhook, threading, argparse
import re

class MouseKeybEvents():
    def __init__(self):
        self.running=True
        self.alt=False
            
#       Принятие аргументов из командной строки
        parser = argparse.ArgumentParser()
        parser.add_argument('-w', '--write', action='store_true', help='режим записи')
        parser.add_argument('-r', '--read', action='store_true', help='режим чтения')
        parser.add_argument('-a', '--alternative', action='store_true', help='''альтернаитвный режим. 
        ЛКМ и ПКМ напрямую распознаються c мыши''')
        parser.add_argument('-f', '--fname', help='Имя файла для работы. Дефолтно это cache.txt')
        args = parser.parse_args()
#       Уже все приняли, дальше пошел процесс создания списка файлов по переданному параметру        
        if args.fname:
            self.filename = args.fname
        if args.alternative:
            self.alt = True
        self.action = {'write':args. write, 'read': args.read}
        
#   Отслеживает положение курсора. Начинает поток th1.
    def traceCoursor(self):
        lastPos=pyautogui.position()
        
        while self.mustFinish == False:
            currPos=pyautogui.position()
            time.sleep(0.1)
            if lastPos == currPos and self.keyPressed == False:
                if self.timerLock == False:
                    self.timerStart()
            else:
#                import pdb;  pdb.set_trace()
                posTime=round(self.timerStop(),1)
                
                self.writeToFile(str(lastPos)+' '+str(posTime)+' NC')
                timerLock=False
                self.resetTimer()
                self.clearTh()
                self.setTh()
                self.waitTh()
                
            lastPos=currPos
        global f
        f.close();print('Файл успешно закрыт')
        
#   Инициализирует метод OnKeyboardEvent. Начинает поток th2.
    def catchKeyPress(self):
            hm = pyxhook.HookManager()
            hm.KeyDown = self.OnKeyboardEvent
            hm.HookKeyboard()
            hm.start()
            while self.running:
                time.sleep(0.1)
            hm.cancel()
            
#    Метод опрелеябщий события нажатия кнопок клавиатуры
    def OnKeyboardEvent(self,event):
            #print(event.Key, event.Ascii)
            if event.Ascii == 32:
                self.running = False
                self.mustFinish = True
            elif event.Key == 'Control_L':
                self.keyPressed=True
                self.clearTh()
                print(self.resumeTh)
                self.waitTh()
                self.writeToFile(str(pyautogui.position())+'0.1 LC')
                self.clearTh()
                self.keyPressed=False
            elif event.Key == 'Shift_L':
                self.keyPressed=True
                self.clearTh()
                self.waitTh()               
                self.writeToFile(str(pyautogui.position())+'0.1 RC')
                self.clearTh()
                self.keyPressed=False
            elif event.Key == 'Alt_L':
                self.keyPressed=True
                self.clearTh()
                self.waitTh()               
                self.writeToFile(str(pyautogui.position())+'0.1 DC')
                self.clearTh()
                self.keyPressed=False            
   
    #Альтернативный метод. Перехват собыйти идет напрямую с мыши
    #------------------------------------------------------
    
    #   Инициализирует метод OnMouseEvent. Начинает поток th3.
    def catchMouseClick(self):
        # create a hook manager
        hm = pyxhook.HookManager()
        # watch for all mouse events
        hm.MouseAllButtonsDown = self.OnMouseEvent
        # set the hook
        hm.HookMouse()
        hm.start()
        while self.running:
            time.sleep(0.1)
        hm.cancel()
            
#    Метод опрелеябщий события кликов мыши
    def OnMouseEvent(self,event):
            self.keyPressed=True
            self.clearTh()
            self.waitTh()        
            #Начался парсинг строки с событием мыши. На выходе переменная act
            #будет иметь значения формата LC или RC
            act='NC'
            message=re.findall(r"(?<=mouse).+?(?=down)", event.MessageName)
            message=message[0].strip()
            if message == 'left':
                act='LC'
            elif message == 'right':
                act='RC'
            elif message == 'middle':
                pass
            #Начался парсинг строки с позицией мыши. На выходе будет кооринаты
            #в переменных x,y
            position=re.findall(r"(?<=\().+?(?=\))", str(event.Position));
            position=(str(position[0])).split(',')
            x=position[0].strip();y=position[1].strip()
            fstring='('+x+', '+y+') 0.1 '+act
            print(fstring)
            try:
                self.writeToFile(fstring)
            except Exception:
                print('не удалось записать')
            self.clearTh()
            self.keyPressed=False

    
    #Закончился альтернативный метод
    #------------------------------------------------------
    
    #Получает строку с кординатами x-y, время задержки курсора и нажатую кнопку мыши.
    #Перемещает курсор с учетом этих характирстик и имитирует клик если это было задано.
    def doMouseMove(self,string):
        try:
            values=string.split(',')
            print(values)
            print(values[0],values[1])
            pyautogui.moveTo(int(values[0]),int(values[1])) #перемщение по кординатам x,y
            delay=float(values[2])
            time.sleep(delay)
            if values[3]=='NC':
                pass
            elif values[3]=='LC':
                pyautogui.click()
            elif values[3]=='RC':
                pyautogui.click(button='right')
            elif values[3]=='DC':
                pyautogui.doubleClick() 
                print('Ожидается DC')
        except IndexError:
            print ('Походу попался перевод каретки')

#   Сей объект класса посвящен таймеру
class Timer(MouseKeybEvents):
    keyPressed=False
    startTime=0
    timerLock=False
    mustFinish=False
    
#    Ставит базовую точку времени с которой начинается отсчет
    def timerStart(self):
        self.timerLock=True
        self.resetTimer()
        self.keyPressed=False
        
#    Останавливает таймер, возвращает разницу времени в секундах между запуском
#    и остановкой
    def timerStop(self):
        self.timerLock=False
        timePassed=time.time() - self.startTime
        
        return timePassed
    
#    Сбрасывает таймер, выставляя значение таймера на 0
    def resetTimer(self):
        self.startTime=time.time()

#Имитация стандартного класса событий, Threading.Events()       
class Locker(MouseKeybEvents):
    delayTh=0.07
    resumeTh=False
    #Заставляет текщий поток ждать пока не появиться флаг о продолжении
    def waitTh(self):
        while True:
            if self.resumeTh==False:
                time.sleep(self.delayTh)
            else:
                break
    #Поднимает флаг, поток возобновляет работу
    def setTh(self):
        self.resumeTh=True
    #Сбрасывает флаг
    def clearTh(self):
        self.resumeTh=False
           
class FileActions():
    filename='cache.as'
    strRecLimit=50 #Предел количества значений в одной строке
    strCounter = strRecLimit
    #Получает строку формата "x,y,время,кнопка мыши", парсит ее на составляющие.
    #Затем пишет в файл. По достижению strRecLimit каретка перескакивает на новую строку.
    def writeToFile(self,string):
        print (string)
        global f
        p = re.findall(r"(\w+\.+\w)|(\w+(?=,))|(\w+(?=\)))|(\w{2})",string)
        #x-кордината, y-кордината, время простоя курсора, кнопка мыши, соответственно
        x=(''.join(p[0])).strip();y=(''.join(p[1])).strip();time=(''.join(p[2])).strip();act=(''.join(p[3])).strip()
        print (x+','+y+','+time+','+act+'\n')
        if self.strCounter >0: 
            f.write(x+','+y+','+time+','+act+';')
            self.strCounter=self.strCounter-1
        else:
            f.write(x+','+y+','+time+','+act+';\n')
            self.strCounter=self.strRecLimit
    
    #Открывает записанный файл, читает его построчно, парсит, выполняет действия.
    def readFromFile(self):
        f = open(self.filename,'r')
        for line in f:
            devideBySemi=line.split(';')
            for value in devideBySemi:
                self.doMouseMove(value)

        f.close();print('Файл успешно закрыт')

class ThreadController(Timer,Locker,FileActions):
    def createThreads(self):
        global f
        f = open(self.filename,'w')
        th1=threading.Thread(target=self.traceCoursor)
        th2=threading.Thread(target=self.catchKeyPress)
        th1.start()
        th2.start()
        if self.alt == True:
            th3=threading.Thread(target=self.catchMouseClick)
            th3.start()
            th3.join()
        th1.join()
        th2.join()        


if __name__ == '__main__':
    a = ThreadController()
    if a.action['write']:
        a.createThreads()
    if a.action['read']:
        a.readFromFile()

       
