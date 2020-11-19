from cmu_112_graphics import *
from tkinter import *
import random
import tkinter as tk
import cv2
import numpy as np
import sys
from pyo import *
import time
import os
import pygame
import pyaudio
import os.path
import threading
import wave
pygame.init()

'''
Citations:
Animation framework: https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#subclassingModalApp
Recording:https://gist.github.com/mabdrabo/8678538
ReadFile and WriteFile functions rewritten by Katja Brackelmanns Puig
Background music:https://freesound.org/people/realtheremin/
Metronome click: http://soundbible.com/tags-click.html

'''
def readFile(path):
    with open(path, "rt", encoding = 'utf8') as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)


class SplashScreenMode(Mode):
    def appStarted(mode):
        pygame.mixer.music.load('BeginningMusic.wav')
        pygame.mixer.music.play(-1)
        url1="https://image.winudf.com/v2/image1/Y29tLmFwcGdyb292ZS5UaGVyZW1pbldhbGxwYXBlcnNfc2NyZWVuXzRfMTU1NDExNDQzNl8wNDM/screen-4.jpg?fakeurl=1&type=.jpg"
        mode.mainImage=mode.loadImage(url1)
        mode.Y=200
        mode.X=400
        mode.r=3
        
    def redrawAll(mode, canvas):
        font = 'Arial 50 bold'
        canvas.create_image(500,500,image=ImageTk.PhotoImage(mode.mainImage))
        canvas.create_text(550,200,text="THEREMAX", fill="red",font=font)
        font = 'Arial 20 bold'
        canvas.create_text(550,300,text="Make music with the wave of your hand!", fill="white", font=font)
        canvas.create_text(550,400, text="Grab something red and green and begin!", fill="white",font=font)
        canvas.create_text(550,600, text="Press any key to continue", fill="white", font=font)


    def keyPressed(mode, event):
        
        mode.app.setActiveMode(mode.app.SelectionMode)

class SelectionMode(Mode):
    def appStarted(mode):
        url1="https://image.winudf.com/v2/image1/Y29tLmFwcGdyb292ZS5UaGVyZW1pbldhbGxwYXBlcnNfc2NyZWVuXzRfMTU1NDExNDQzNl8wNDM/screen-4.jpg?fakeurl=1&type=.jpg"
        mode.mainImage=mode.loadImage(url1)
        mode.InputCorrect=None
        mode.InputTaken=False
        mode.tempo=0
        mode.midFreq=0
        mode.octave=0
    
    #reask() copied and modified from https://www.python-course.eu/tkinter_entry_widgets.php
    def reask(mode):
        mode.InputTaken=True
        #Takes tempo, middlefrequency and octave as input from the user
        def getValues():
            #Extacts values from GUI and stores it in data members
            mode.tempo=tempo.get()
            mode.midFreq=midFreq.get()
            mode.octave=octave.get()
            if(not mode.satisfiesConstraints()):
                mode.InputCorrect=False
                #mode.reask()
            else:
                mode.InputCorrect=True

            
        inputs = tk.Tk()
        tk.Label(inputs, text="Tempo").grid(row=0)
        tk.Label(inputs, text="Middle Note").grid(row=1)
        tk.Label(inputs, text="Octave").grid(row=2)
        

        tempo = tk.Entry(inputs)
        midFreq = tk.Entry(inputs)
        octave = tk.Entry(inputs)
        

        tempo.grid(row=0, column=1)
        midFreq.grid(row=1, column=1)
        octave.grid(row=2, column=1)
        tk.Button(inputs, 
          text='Save', command=getValues).grid(row=3,column=1,sticky=tk.W,pady=4)
        
            
        
    def redrawAll(mode, canvas):
        canvas.create_image(500,500,image=ImageTk.PhotoImage(mode.mainImage))
        font = 'Arial 50 bold'
        canvas.create_text(500,50,text="TUNING", fill="white",font=font)
        font="Arial 30 bold"
        canvas.create_text(500,200, text="a. Select a tempo (1-150)",fill="white",font=font)
        canvas.create_text(550,300,text="b. Select a middle frequency - Any valid note (in caps)", fill="white",font=font)
        canvas.create_text(500,400, text="c. Select a octave (1-15)",fill="white",font=font)
        canvas.create_rectangle(450,500,550,550, fill="red")
        canvas.create_text(500,525,text="SELECT", fill="white")
        if(mode.InputCorrect==False):
            mode.displayErrorMessage(canvas)
        elif(mode.InputTaken and mode.InputCorrect):
            mode.displayGoodMessage(canvas)
        
    def mousePressed(mode,event):
        #Asks user for input based on mouse press
        if(event.x>=450 and event.x<=550 and event.y>=500 and event.y<=550):
            if(not mode.InputTaken):
                mode.reask()

    def keyPressed(mode, event):
        if(mode.InputCorrect):
            pygame.mixer.music.stop()
            mode.transferVariables(mode.app.gameMode)
            mode.app.setActiveMode(mode.app.gameMode)

    def satisfiesConstraints(mode):
        #Makes sure the user input is valid. Returns False if not
        try:
            mode.tempo=int(mode.tempo)
        except:
            return False
        try:
            mode.octave=int(mode.octave)
        except:
            return False
        con1=isinstance(mode.tempo,int) or isinstance(mode.tempo,float)
        con2=(mode.tempo<=150 and mode.tempo>=0)
        con3=(isinstance(mode.octave,int))
        con4=(mode.octave>0 and mode.octave<15)
        con5=mode.midFreq in ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
        res=(con1 and con2 and con3 and con4 and con5)
        return(res)
    def displayErrorMessage(mode,canvas):
        font="Arial 20 bold"
        canvas.create_text(500,600, text="One or more parameters are invalid. Try again", fill="yellow",font=font)
    def displayGoodMessage(mode,canvas):
        font="Arial 20 bold"
        canvas.create_text(500,600, text="You're all set! Press any key to continue", fill="green",font=font)
    def transferVariables(mode,GameObject):
        GameObject.tempo=mode.tempo
        GameObject.midFreq=mode.midFreq
        GameObject.octave=mode.octave
    
class GameMode(Mode):
    def appStarted(mode):
        url1="https://image.winudf.com/v2/image1/Y29tLmFwcGdyb292ZS5UaGVyZW1pbldhbGxwYXBlcnNfc2NyZWVuXzRfMTU1NDExNDQzNl8wNDM/screen-4.jpg?fakeurl=1&type=.jpg"
        mode.mainImage=mode.loadImage(url1)
        mode.isInitialized=False
        #Has 'Start' been pressed yet?
        mode.hasStarted=False
        #Current position, frequency and note
        mode.CurrentPos=-1
        mode.CurrentFreq=-1
        mode.CurrentNote=-1
        #Dimensions of the tkinter canvas wherethe lines will be drawn
        mode.PixelsX=700
        mode.PixelsY=700
        #Tuned note dictionary
        mode.tuning=dict()
        #Distance of betwwen two notes on the canvas
        mode.dist_notes=-1
        #Green Position
        mode.UpperMostSpot=-1
        mode.isRecording=False
    def setVolToImage(mode,img):
        #Configures different Y values of the image to different volume settings
        mode.Volumes=[]
        rows,cols,channels=img.shape
        #every slicelength rows, the volume shifts 0.3
        #numbers 15 and 0.3 has been chosen after some testing
        sliceLength=rows/15
        i=1
        #Maximum volume=5
        Vol=5
        while i<15:
            position=i*sliceLength
            Volume=Vol
            #Adding a volume setting to the volume dictionary
            mode.Volumes.append((position,Volume))
            i+=1
            Vol-=0.3
    def PlayBeat(mode):
        beat = pygame.mixer.Sound('Click.wav')
        #The time interval between two beats
        gap = 60.0 / mode.tempo
        while True:
            beat.play()
            time.sleep(gap)
    
        #Ideally, the while loop should run for the same duration in every iteration and hence, is a sound algorithm to play a metronome
        #In reality, the duration of the iteration depends on the processor speed and number of applications running in the background.
        #Hence,the beat could lag occasionally
                    


    def findLeftMostRedSpot(mode,img):
        #Finds the left most red pixel in order to determine the note
        rows, cols,channels=img.shape
        maxX=0
        for col in range(cols-1):
            #Slices a 2D list into columns and tests for red
            if(img[:,col:col+1,0].max()>100):
                maxX=col
                break
        return maxX

    def findUpperMostGreenSpot(mode,img):
        #Finds the uppermost green spot to determine the volume
        rows, cols,channels=img.shape
        maxX=-1
        for row in range(rows-1):
            #Slices a 2D list into rows and tests for green
            if(img[row:row+1,:,1].max()>100):
                maxX=row
                break
        return maxX

    def Tuning(mode,img):
        #Multiplying the base frequency by powers of 2 produces notes of different octaves
        multFactor=2**(mode.octave-3)
        tuningLeftHalf=[]
        tuningRightHalf=[]    
        tuning=[]
        #Base frequency dictionary
        NotesToFrequency=[("C",130.82),("C#",138.59), ("D",146.83),("D#",155.56),("E",164.81),
                          ("F",174.61), ("F#",185), ("G",196), ("G#",207.65),
                          ("A",220), ("A#",233.08),("B",246.94)]
        #Tunes with respect to midFrequency
        for i in range(len(NotesToFrequency)):
            note,freq=NotesToFrequency[i]
            if(note==mode.midFreq):
                ArrayPosition=i
        mode.PixelsX=img.shape[1]
        #The distance between two notes on the image
        mode.dist_notes=mode.PixelsX/25
        position=mode.PixelsX//2
        i=ArrayPosition
        #Position of the note to the left of the middle note
        posBeg=position-mode.dist_notes
        multFactorLeft=multFactor
        while(posBeg>0):
            #"Tunes" the left half of the image
            note,freq=NotesToFrequency[(i-1)%12]
            #moving down a scale, if we encounter a B, the following notes are all an octave lower
            if(note=="B"):
                multFactorLeft=0.5*multFactor
            tuningLeftHalf.append((posBeg,note,freq*multFactorLeft))
            i-=1
            #Tuning backwards
            posBeg-=mode.dist_notes
        multFactorRight=multFactor
        i=ArrayPosition
        while(position<mode.PixelsX):
            #"Tunes" the right half of the image
            note,freq=NotesToFrequency[i%12]
            #If a C is encountered and it is not the middle note, the following notes are in the higher octave
            if(i!=ArrayPosition and note=="C"):
                multFactorRight=2*multFactor
            tuningRightHalf.append((position,note,freq*multFactorRight))
            position+=mode.dist_notes
            #This list is populated from right to left
            i+=1
        mode.tuning=tuningLeftHalf[::-1]+tuningRightHalf
        mode.isInitialized=True
        #The left half is tuned in reverse and hence needs to be reversed before it is added to the right side


    def PlayTheTheremin(mode):
        #OpenCV code learnt from https://pythonprogramming.net/color-filter-python-opencv-tutorial/
        #A cv will be added next to the lines I got from the website
        #Sound related code learnt from http://ajaxsoundstudio.com/pyodoc/gettingstarted.html
        #A pyo will be added next to lines I got from the website
        cam = cv2.VideoCapture(0)#cv
        FirstImage=True
        s = Server().boot()#pyo
        a = Sine(1, 0, 0.1).out()#pyo
        s.start()#pyo
        while True:
            ret,frame=cam.read()#cv
            if(FirstImage):
                #Tuning happens based on the dimensions of the first image.
                mode.Tuning(frame)
                mode.setVolToImage(frame)
                FirstImage=False
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)#cv
        
            lower_red = np.array([0, 140, 70])#cv
            upper_red = np.array([10, 255, 255])#cv
            lower_green = np.array([36,100,50])
            upper_green = np.array([88,255,255])
            mask = cv2.inRange(hsv, lower_red, upper_red)#cv
            res = cv2.bitwise_and(frame,frame, mask= mask)#cv
            maskG = cv2.inRange(hsv, lower_green, upper_green)
            resG = cv2.bitwise_and(frame,frame, mask= maskG)
            #Pitch control
            leftMostPoint=mode.findLeftMostRedSpot(res)
            #Volume control
            mode.UpperMostSpot=mode.findUpperMostGreenSpot(resG)
            
            cols=res.shape[1]
            #The recording is laterally inverted and pitch increases as the red object moves to the left in the image
            mode.LaterallyInverted=cols-leftMostPoint
            mode.CurrentPos=mode.LaterallyInverted
            for position in range(len(mode.tuning)-1):
                #finding the x-position on the screen and mapping and setting the appropriate frequency to the stream
                if mode.LaterallyInverted>=mode.tuning[position][0] and mode.LaterallyInverted<=mode.tuning[position+1][0]:
                    pos,note,freq=mode.tuning[position]
                    freq=freq//1
                    mode.CurrentNote=note
                    mode.CurrentFreq=freq
                    a.setFreq(freq)
            #If there is no green object in the image, the volume of the stream is zero
            if(mode.UpperMostSpot==-1):
                a.mul=0
            else:
                for position in range(len(mode.Volumes)-1):
                    #finding the y-position on the screen and mapping and setting the appropriate volume to the stream
                    if mode.UpperMostSpot>=mode.Volumes[position][0] and mode.UpperMostSpot<=mode.Volumes[position+1][0]:
                        pos,vol=mode.Volumes[position]
                        a.mul=vol

            cv2.waitKey(1)
            if(ret==False):
                break
    def getfileNumber(mode,path):
        #All the recordings are numbered in the increasing order with the latest one having the maximum number
        #To create a new file, we find the maximum numbered existing file. We add 1 to that number to craete a new file
        maxNum = 0
        for filename in os.listdir(path):
            #Does the filename start with a number?
            if filename[0].isdigit():
                #Is it the maximum number?
                if int(filename[0])>maxNum:
                    maxNum = int(filename[0])
        #Returns the next number for the new file
        return maxNum +1
    def RecordSound(mode):
         
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = 5
        newFileNumber=mode.getfileNumber(os.getcwd())
        #new audio file in the current directory
        WAVE_OUTPUT_FILENAME = str(newFileNumber)+".wav"
         
        audio = pyaudio.PyAudio()
         
        # start Recording
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
        frames = []

        #I wrote the while loop
        #Instead of taking a specific duration, we keep recording as long as isRecording is True.
        #isRecording is manipulated in keyPressed
        
        while(True):
            if(mode.isRecording):
                data = stream.read(CHUNK)
                frames.append(data)
            else:
                break
         
         
        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()
        #The file is created and stored
        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()


    
    def keyPressed(mode, event):
        if (event.key == 'h'):
            mode.app.setActiveMode(mode.app.helpMode)
        elif(event.key=='r' and not mode.isRecording):
            mode.isRecording=True
            #recording is done in parallel with the theremin playing 
            record=threading.Thread(target=mode.RecordSound)
            record.start()
        elif(event.key=='r'):
            mode.isRecording=False
    def mousePressed(mode,event):
        if(event.x>=350 and event.x<=650 and event.y>=300 and event.y<=400):
            mode.hasStarted=True
            #theremin is played in parallel with the running animation framework 
            theremin = threading.Thread(target=mode.PlayTheTheremin)
            #the metronome runs in parallel with the framework and the theremin
            metronome = threading.Thread(target=mode.PlayBeat)
            theremin.start()
            metronome.start()
        if(event.x>=700 and event.x<=900 and event.y>=25 and event.y<=75):
            
            mode.app.setActiveMode(mode.app.ListFiles)
            

    def redrawAll(mode, canvas):
        if(not mode.hasStarted):
            font="Arial 20 bold"
            canvas.create_image(500,500,image=ImageTk.PhotoImage(mode.mainImage))
            canvas.create_rectangle(350,300,650,400, fill="red")
            canvas.create_text(500,350,text="START", fill="white",font=font)
        
        elif(not mode.isInitialized):
            #Until the main variables have been initialized, nothing can happen
            canvas.create_image(500,500,image=ImageTk.PhotoImage(mode.mainImage))
        else:
            canvas.create_image(500,500,image=ImageTk.PhotoImage(mode.mainImage))
            ratioX=800/mode.PixelsX
            ratioY=700/mode.PixelsY
            NewDistance=ratioX*mode.dist_notes
            pos=1
            for position,note,freq in mode.tuning:
                #draws the note lines
                if(note==mode.CurrentNote and abs(mode.CurrentPos-position)<20):
                    #Current note is highlighted in green
                    canvas.create_line(pos*NewDistance,100,pos*NewDistance,600,width=5, fill="green")
                else:
                    canvas.create_line(pos*NewDistance,100,pos*NewDistance,600,width=5, fill="white")
                canvas.create_text(pos*NewDistance,620,text=note,fill="yellow")#note names
                pos+=1
            #The note pointer
            pointerX=ratioX*mode.CurrentPos
            #If there is no green in the image, the volume bar reads zero
            if(mode.UpperMostSpot==-1):
                pointerY=600
            else:
                pointerY=ratioY*mode.UpperMostSpot
            #The yellow dot pointer
            canvas.create_oval(pointerX-10,pointerY-10,pointerX+10,pointerY+10,fill="yellow")
            
            canvas.create_rectangle(900,pointerY,950,600,fill="green")
            #The volume bar
            font="Arial 20 bold"
            if(mode.isRecording):
                canvas.create_text(100,50,text="Recording...",fill="green",font=font)
            else:
                canvas.create_text(200,50,text="Press 'r' to record",fill="red",font=font)
            canvas.create_rectangle(700,25,900,75,fill="white")
            canvas.create_text(800,50,text="View recordings")
            canvas.create_text(550,50,text="Press 'h' for help",font=font,fill="white")
            
           
class ListFilesMode(Mode):
    def appStarted(mode):
        url1="https://image.winudf.com/v2/image1/Y29tLmFwcGdyb292ZS5UaGVyZW1pbldhbGxwYXBlcnNfc2NyZWVuXzRfMTU1NDExNDQzNl8wNDM/screen-4.jpg?fakeurl=1&type=.jpg"
        mode.mainImage=mode.loadImage(url1)
        mode.X=450
        mode.Y=100
        mode.files=[]
        mode.getFileList(os.getcwd())
    def getFileList(mode,path):
        #Gets all the numbered files in the current directory
        for filename in os.listdir(path):
            if filename[0].isdigit():
                mode.files.append(filename)
        
    def redrawAll(mode, canvas):
        x=mode.X
        y=mode.Y
        font="Arial 26 bold"
        
        canvas.create_image(500,500,image=ImageTk.PhotoImage(mode.mainImage))
        canvas.create_text(550,50, text="RECORDINGS", fill="white",font=font)
        for file in mode.files:
            #CReates buttons for each file
            canvas.create_rectangle(x,y,x+200,y+50, fill="white")
            canvas.create_text(x+100,y+25,text=file,fill="black")
            y+=55
        font="Arial 20 bold"
        canvas.create_text(550,550, text="Press any key to make another recording!",fill="white",font=font)
        

    def keyPressed(mode,event):
        mode.app.setActiveMode(mode.app.gameMode)
    def mousePressed(mode,event):
        x=mode.X
        y=mode.Y
        for file in mode.files:
            #Checks if any file has been clicked on (to play the piece)
            if(event.x>x and event.x<x+200 and event.y>y and event.y<y+50):
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
            y+=55

class HelpMode(Mode):
    def appStarted(mode):
        url1="https://image.winudf.com/v2/image1/Y29tLmFwcGdyb292ZS5UaGVyZW1pbldhbGxwYXBlcnNfc2NyZWVuXzRfMTU1NDExNDQzNl8wNDM/screen-4.jpg?fakeurl=1&type=.jpg"
        mode.mainImage=mode.loadImage(url1)
        mode.Y=200
        mode.X=400
        mode.r=10
        mode.dX=10
        mode.dY=10
    def redrawAll(mode, canvas):
        font = 'Arial 26 bold'
        canvas.create_image(500,500,image=ImageTk.PhotoImage(mode.mainImage))
        canvas.create_text(mode.width/2, 150, text='Did someone say Help?', font=font,fill="white")
        font = 'Arial 20 bold'
        canvas.create_text(mode.width/2, 250, text='Move a red object from left to right to control pitch!', font=font, fill="red")
        canvas.create_text(mode.width/2, 300, text='Move a green object up and down to control volume!', font=font, fill="green")
        canvas.create_text(mode.width/2, 400, text='Press any key to continue playing', font=font, fill="white")
        canvas.create_oval(200-mode.r,mode.Y-mode.r,200+mode.r,mode.Y+mode.r, fill="green")
        canvas.create_oval(mode.X-mode.r,500-mode.r,mode.X+mode.r,500+mode.r,fill="red")

    def timerFired(mode):
        #Moves green dot up and down
        #Moves red dot sideways
        if(mode.X>900):
            mode.dX=-10
        elif(mode.X<400):
            mode.dX=10
        if(mode.Y>600):
            mode.dY=-10
        elif(mode.Y<200):
            mode.dY=10
        #Bouncing motion implemented
        mode.Y+=mode.dY
        mode.X+=mode.dX
        

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.gameMode)

class MyModalApp(ModalApp):
    def appStarted(app):
        app.splashScreenMode = SplashScreenMode()
        app.SelectionMode=SelectionMode()
        app.gameMode = GameMode()
        app.ListFiles=ListFilesMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.splashScreenMode)
        app.timerDelay = 50

app = MyModalApp(width=1150, height=1000)


