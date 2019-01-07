## A non-acedemic project by Mazeyar Moeini Feizabadi with the help of
## countless online recourses. The most valuable of them being Christian Diener
## https://gist.github.com/cdiener with his simple asciinator algorithm.
##



import sys
from PIL import Image,ImageDraw
import os
import shutil
import numpy as np
from matplotlib import pyplot as plt
import cv2
import natsort


## Start by creating an object of your video
## cat = asciiArt("catvideosample.mp4")
## adjust the video's gamma and rotation
## cat.setGamme(int gamma)
## cat.rotation(int angle)
## render the object
## cat.render("<outputname>")
## delete unnecessary files
## cat.close()


class asciiVideo:
    
    gamma = 1.55
    scale = .1
    rotation = 0
    widthScale , lengthScale = 1,1
    adjust = False
    chars = np.asarray(list('    `.,:;+&#@'))
    widthFrame, lengthFrame = 0,0
    text_width, text_length = 0,0
    fps = 30
    frame = 0
    
    #Constructor 
    def __init__(self, videoName):
        self.videoName = videoName
        self.videoFolder = videoName + "Frames"
        self.asciiFolder = videoName + "AsciiFames"
        self.createFolder(self.videoFolder)
        self.frameCapture()
        self.sample(0,True)
        
    #Destructor
    def __del__(self):
        print("Deleting all unnecessary folders and memory")
        shutil.rmtree(self.videoFolder)
        try:
            shutil.rmtree(self.asciiFolder)
        except:
            pass
        
    #Folder creator 
    def createFolder(self, name):
        if not os.path.exists(name):
            os.makedirs(name)
        else:
            shutil.rmtree(name)
            os.makedirs(name)
    
    #Function to extract frames from video
    def frameCapture(self):    
        # Path to video file 
        vidObj = cv2.VideoCapture(self.videoName)
        
        self.fps = vidObj.get(cv2.CAP_PROP_FPS)
        # Used as counter variable 
        count = 0
        # checks whether frames were extracted 
        success = 1
        while success: 
            # vidObj object calls read 
            # function extract frames 
            try:
                success, image = vidObj.read() 
                # Saves the frames with frame-count 
                
                rows,cols = image.shape[0],image.shape[1]
                rotationMatrix = cv2.getRotationMatrix2D((cols/2,rows/2),self.rotation,1)
                image = cv2.warpAffine(image,rotationMatrix,(cols,rows))
                
                cv2.imwrite(self.videoFolder+"/frame%d.png" % count, image) 
                
                count += 1
            except:
                break
            
    
    def sample(self, frame=0, show=False):
    
        self.frame = frame
        
        #Makes sure this function runs onces to adjust the diemensions 
        if not self.adjust:
            img = Image.open(self.videoFolder+"/frame%d.png" % frame)
            #img.show()
            
            self.widthFrame = img.size[0]
            self.lengthFrame = img.size[1]
            
            ##Make image into ascii text matrix
            width = round(self.widthFrame*self.scale*self.widthScale)
            height = round(self.lengthFrame*self.scale*self.lengthScale) 
            size = ( width,  height)
            img = np.sum( np.asarray( img.resize(size) ), axis=2)
            img -= img.min()
            img = (1.0 - img/img.max())**self.gamma*(self.chars.size-1)
        
            text = "\n".join( ("".join(r) for r in  self.chars[img.astype(int)]))
            
            ##create sample to find diemensions of text
            textImage = Image.new('RGB', (200, 100))
            d = ImageDraw.Draw(textImage)
            d.text((0,0), text, fill=(255, 0, 0))
            self.text_width, self.text_length = d.textsize(text)
            print(self.text_width,self.text_length,self.widthFrame ,self.lengthFrame)
            
            
            #rescale to fit given video format
            self.widthScale = self.widthFrame/self.text_width
            self.lengthScale = self.lengthFrame/self.text_length
            self.text_width =  round(self.text_width*self.widthScale)
            self.text_length = round(self.text_length*self.lengthScale)
            self.adjust = True
        
        
        
        img = Image.open(self.videoFolder+"/frame%d.png" % frame)
        img = img.rotate(self.rotation)
        
        
        #remake ascii matrix scales
        width = round(self.widthFrame*self.scale*self.widthScale)
        height = round(self.lengthFrame*self.scale*self.lengthScale) 
        size = (width, height)
        print(size,"size")
        
        #apply  image filter
        imag = np.sum( np.asarray( img.resize(size) ), axis=2)
        imag -= imag.min()
        imag = (1.0 - imag/imag.max())**self.gamma*(self.chars.size-1)
    
        text = "\n".join( ("".join(r) for r in self.chars[imag.astype(int)]))
        
        #redraw image with correct diemensions
        textImage = Image.new('RGB', (self.text_width,self.text_length),(255,255,255))
        d = ImageDraw.Draw(textImage)
        d.text((0,0), text, fill=(0, 0, 0))
        
        print(self.text_width,self.text_length,self.widthFrame ,self.lengthFrame)
        
        if show:
            img.show()
            textImage.show()
        return textImage
    
    
    #takes the folder of frames and makes them into a folder of ascii frames
    def transform(self):
        
        
        self.createFolder(self.asciiFolder)
        
        #returns item names in video frame folder
        images = self.returnFolderItems(self.videoFolder)
        
        
        # for each frames of the video this loop runs the ascii algorithm
        #and put that in a seperate folder
        for image in images:
            
            img = Image.open(self.videoFolder+"/%s" % image)
            img = img.rotate(self.rotation)
            
            width = round(self.widthFrame*self.scale*self.widthScale)
            height = round(self.lengthFrame*self.scale*self.lengthScale) 
            size = (width, height)
            
            imag = np.sum( np.asarray( img.resize(size) ), axis=2)
            imag -= imag.min()
            imag = (1.0 - imag/imag.max())**self.gamma*(self.chars.size-1)
        
            text = "\n".join( ("".join(r) for r in self.chars[imag.astype(int)]))
            
            #redraw image
            textImage = Image.new('RGB', (self.text_width,self.text_length),(255,255,255))
            d = ImageDraw.Draw(textImage)
            d.text((0,0), text, fill=(0, 0, 0))
            textImage.save(self.asciiFolder+"/%s" % image)
            
    #Takes every ascii frame and makes that into a video file
    def render(self, outputname):
    
        self.transform()
        video_name = outputname+'.mp4'
        try:
            os.unlink(video_name)
        except:
            pass
        
        path = self.asciiFolder
        images = self.returnFolderItems(path)
         
        frame = cv2.imread(os.path.join(path+"/", images[0]))
        height, width, layers = frame.shape
        
        video = cv2.VideoWriter(video_name, -1, self.fps, (width,height))
        print("Compiling %d images" % len(images))
        for image in images:
            video.write(cv2.imread(os.path.join(path+"/", image)))
        
        cv2.destroyAllWindows()
        video.release()
        
    #close method for destructor
    def close(self):
        self.__del__()
                
    #set gamma of frame and return sample
    def setGamma(self, gamma):
        self.gamma = gamma
        return self.sample(self.frame)
    
    #set rotation of frame and return sample
    def setRotation(self, angle):
        self.rotation = angle
        return self.sample(self.frame)       

    def returnFolderItems(self,path):
        image_folder = path+"/"
        images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
        images = natsort.natsorted(images)
        return images
