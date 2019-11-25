import tkinter as tk
from tkinter import*
import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font

def PageOne():
    top = Toplevel()
    top.geometry("1000x1000+120+120")    
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass 
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass 
        return False

    def TakeImages():        
        Id=(txt.get())
        name=(txt2.get())
        if(is_number(Id) and name.isalpha()):
            cam = cv2.VideoCapture(0)
            harcascadePath = "haarcascade_frontalface_default.xml"
            detector=cv2.CascadeClassifier(harcascadePath)
            sampleNum=0
            while(True):
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x,y,w,h) in faces:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        
                    sampleNum=sampleNum+1
                    cv2.imwrite("TrainingImage\ "+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                    cv2.imshow('frame',img)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                elif sampleNum>60:
                    break
            cam.release()
            cv2.destroyAllWindows() 
            res = "Images Saved for ID : " + Id +" Name : "+ name
            row = [Id , name]
            with open('StudentDetails\StudentDetails.csv','a+') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(row)
            csvFile.close()
            message.configure(text= res)
        else:
            if(is_number(Id)):
                res = "Enter Alphabetical Name"
                openpage.configure(text= res)
            if(name.isalpha()):
                res = "Enter Numeric Id"
                message.configure(text= res)
    def TrainImages():
        recognizer = cv2.face_LBPHFaceRecognizer.create()
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector =cv2.CascadeClassifier(harcascadePath)
        faces,Id = getImagesAndLabels("TrainingImage")
        recognizer.train(faces, np.array(Id))
        recognizer.save("TrainingImageLabel\Trainner.yml")
        res = "Image Trained"
        message.configure(text= res)
    def getImagesAndLabels(path):
        imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
        faces=[]
        Ids=[]
        for imagePath in imagePaths:
            pilImage=Image.open(imagePath).convert('L')
            imageNp=np.array(pilImage,'uint8')
            Id=int(os.path.split(imagePath)[-1].split(".")[1])
            faces.append(imageNp)
            Ids.append(Id)        
        return faces,Ids
    button = Button(top, text="Take", width=10 ,fg="red"  ,bg="yellow" ,font=('times', 15), command=lambda:TakeImages())
    button.place(x=50,y=300)
    button = Button(top, text="Train",  width=10 ,fg="red"  ,bg="yellow" ,font=('times', 15),command=lambda:TrainImages())
    button.place(x=50,y=200)
    lbl = tk.Label(top, text="Enter ID : ",width=20 ,fg="red"  ,bg="yellow" ,font=('times', 15, ' bold ') ) 
    lbl.place(x=250, y=150)
    txt = tk.Entry(top,width=20  ,bg="yellow" ,fg="red",font=('times', 15, ' bold '))
    txt.place(x=550, y=150)
    lbl2 = tk.Label(top, text="Enter Name : ",width=20  ,fg="red"  ,bg="yellow" ,font=('times', 15, ' bold ')) 
    lbl2.place(x=250, y=250)
    txt2 = tk.Entry(top,width=20  ,bg="yellow"  ,fg="red",font=('times', 15, ' bold ')  )
    txt2.place(x=550, y=265)
    lbl3 = tk.Label(top, text="Status : ",width=20  ,fg="red"  ,bg="yellow"  ,font=('times', 15)) 
    lbl3.place(x=250, y=350)
    message = tk.Label(top, text="" ,bg="yellow"  ,fg="red"  ,width=20  ,activebackground = "yellow" ,font=('times', 15, ' bold ')) 
    message.place(x=550, y=350)
    button = Button(top, text="Home", width=10 ,fg="red"  ,bg="yellow" ,font=('times', 15), command=top.destroy)
    button.place(x=200,y=500)
    button = Button(top, text="Track", width=10 ,fg="red"  ,bg="yellow" ,font=('times', 15), command=lambda:[top.destroy(),PageTwo()])
    button.place(x=550,y=500)
    top.resizable(0,0)

def PageTwo():
    top = Toplevel()
    top.geometry("1000x1000+120+120")
    def TrackImages():
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("TrainingImageLabel\Trainner.yml")
        harcascadePath = "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath);    
        df=pd.read_csv("StudentDetails\StudentDetails.csv")
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX        
        col_names =  ['Id','Name','Date','Time']
        attendance = pd.DataFrame(columns = col_names)    
        while True:
            ret, im =cam.read()
            gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            faces=faceCascade.detectMultiScale(gray, 1.2,5)    
            for(x,y,w,h) in faces:
                cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
                Id, conf = recognizer.predict(gray[y:y+h,x:x+w])                                   
                if(conf < 50):
                    ts = time.time()      
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    aa=df.loc[df['Id'] == Id]['Name'].values
                    tt=str(Id)+"-"+aa
                    attendance.loc[len(attendance)] = [Id,aa,date,timeStamp]
                else:
                    Id='Unknown'                
                    tt=str(Id)  
                if(conf > 75):
                    noOfFile=len(os.listdir("ImagesUnknown"))+1
                    cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
                cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)        
            attendance=attendance.drop_duplicates(subset=['Id'],keep='first')    
            cv2.imshow('im',im) 
            if (cv2.waitKey(1)==ord('q')):
                break
        ts = time.time()      
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour,Minute,Second=timeStamp.split(":")
        fileName="Attendance\Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
        attendance.to_csv(fileName,index=False)
        cam.release()
        cv2.destroyAllWindows()
        res=attendance
        message2.configure(text= res)
    lbl3 = tk.Label(top, text="Details : ",width=20  ,fg="red"  ,bg="yellow"  ,font=('times', 15)) 
    lbl3.place(x=150, y=300)
    button = Button(top, text="Track", width=20 ,fg="red"  ,bg="yellow" ,font=('times', 15),command=lambda:TrackImages())
    button.place(x=150,y=150)
    message2 = tk.Label(top, text="" ,fg="red"   ,bg="yellow",activeforeground = "green",width=20  ,font=('times', 15)) 
    message2.place(x=450, y=300)
    button = Button(top, text="Home", width=10 ,fg="red"  ,bg="yellow" ,font=('times', 15), command=top.destroy)
    button.place(x=200,y=500)
    button = Button(top, text="Take and Train", width=20 ,fg="red"  ,bg="yellow" ,font=('times', 15), command=lambda:[top.destroy(),PageOne()])
    button.place(x=550,y=500)
    top.resizable(0,0)   
root = Tk()
lbl = tk.Label(root, text="Virtual Attendance System",width=20 ,fg="red",font=('times', 25) ) 
lbl.place(x=150, y=100)
button = Button(root, text="Take and Train", width=20 ,fg="red"  ,bg="yellow" ,font=('times', 15) ,command=PageOne)
button.place(x=200,y=250)
button = Button(root, text="Track",width=20 ,fg="red"  ,bg="yellow" ,font=('times', 15), command=PageTwo)
button.place(x=200,y=325)
button = Button(root, text="Quit",width=20 ,fg="red"  ,bg="yellow" ,font=('times', 15), command=root.destroy)
button.place(x=200,y=400)
root.geometry("600x600+120+120")
root.resizable(0,0)
root.mainloop()
