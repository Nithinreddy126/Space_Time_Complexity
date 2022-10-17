import sys 
import os
import multiprocessing 
cwd = os.getcwd()
sys.path.append(cwd)
import cv2 as cv 
from pathlib import Path
import subprocess
from scenedetect import detect, ContentDetector
from sys import platform
import Classification.Inter_intra_classification as ii

class SceneDetect :
    
    def __init__(self,video_path:str,yuvformat,Psnr,Vmaf):
        
        # variable declaration
        self.video_path = video_path
        self.yuvformat=yuvformat
        self.Psnr=Psnr
        self.Vmaf=Vmaf

    def getSceneList(self):
        # get scene list
        self.scene_list = detect(self.video_path, ContentDetector())
        x,y=[],[]
        start_time,end_time,nframes=[],[],[]
        for i in range (len(self.scene_list)):
            
               start_time.append((self.scene_list[i][0])) # starting time and frame of each scene
               end_time.append(self.scene_list[i][1]) # ending time and frame of each scene
               x.append(str(start_time[i])) # Starting time code 
               y.append(str(end_time[i])) # ending time code
               nframes.append(int(end_time[i]))# Last frame number of each scene
        self.scene_parameters=(x, y, len(self.scene_list),nframes,self.scene_list)
        return 1

    def video_dims(self):
        # get video Resolution
        vcap = cv.VideoCapture(self.video_path)

        if vcap.isOpened(): 
            width  = int(vcap.get(cv.CAP_PROP_FRAME_WIDTH))   # float `width`
            height = int(vcap.get(cv.CAP_PROP_FRAME_HEIGHT))  # float `height`        
            self.Res=[width,height]

    def yuv_Conversion(self,Scene_name,start_time,end_time):
        
        if platform == "win32": shell = False #windows
        else: shell = True  #linux 
        # create command to use ffmpeg to convert scenes to yuv 
        return subprocess.call(f'ffmpeg -y -i {self.video_path} -c:v rawvideo -s {self.Res[0]}x{self.Res[1]} -pix_fmt {self.yuvformat} -ss {start_time} -t {end_time} {Scene_name}.yuv  -loglevel 0' , shell=shell) 
            
    

    def get_complexiy(self,i):
        # calculate the duration of scene
        start_time=self.scene_parameters[0][i]
        #convert time code to seconds
        h,m,s= start_time.split(':')
        sec1=int(h)*3600+int(m)*60+ float(s)
        end_time=self.scene_parameters[1][i]
        h,m,s= end_time.split(':')
        sec2=int(h)*3600+int(m)*60+ float(s)
        # substract end time and start time to get duration
        diff=sec2-sec1
        #convert seconds to timecode
        hr1=diff % 3600
        hh,mm,ss=diff//3600,hr1//60,hr1%60
        hh="{:02d}".format(int(hh))
        mm="{:02d}".format(int(mm))
        ss="{:06.3f}".format(ss)
        end_time=(f'{hh}:{mm}:{ss}')
            
        nframes=self.scene_parameters[3][i]-self.scene_parameters[3][i-1]
        m=i+1
        if i < 1: nframes=self.scene_parameters[3][i]
        scene_name=Path(self.video_path).stem + str(m)
                
        if (nframes>30):
            if nframes>500: end_time='00:00:10' # 10 seconds duration for scene longer that 10 seconds
            return_value=self.yuv_Conversion(scene_name,start_time,end_time) # send scene1 to conver to yuv
            if return_value: print(f'Cannot convert scene {m} to yuv ') 
            else:
                if nframes>500:nframes=500# 500 frames for scene longer that 10 seconds
                classification=ii.intra_inter_classification(scene_name+'.yuv',self.Res,self.yuvformat,0,nframes)
                cls=classification.get_intra_inter(m) #send scene for complexity classification
                # call for QP suggestion for complexity   
                qp_vmaf=Coding_Parameter.VMAF(self.Vmaf,cls[0],cls[1])
                qp_psnr=Coding_Parameter.PSNR(self.Psnr,cls[0],cls[1])

                if self.save == 'N':os.remove(f'{scene_name}.yuv')# delete the yuv file of scene 
                print(f'{m} : [{self.scene_list[0]}    {cls[0]}    {cls[1]}    {qp_vmaf}    {qp_psnr}]')
                return [m,nframes,cls[0],cls[1],qp_vmaf,qp_psnr]        
        
            
    def threads_idx(self,save):
        # start=time.time() # save starting time
        return_val = self.getSceneList()
        self.video_dims()
        
        if return_val:
            nScene=len(self.scene_list)
            print(f'{nScene} scenes detected')
            
            self.save=save
            #cearte threads for multiprocessing
            with multiprocessing.Pool(4) as pool:
                results= pool.map(self.get_complexiy,iterable=[i for i in range(nScene)])
            return [results,nScene,self.scene_list]
        else: print(f'Could not detect scenes')


class Coding_Parameter :

    def VMAF(VMAF,intra,inter):
        #vmaf optimat QP
        Vmaf=[[[34,24,23,23], [37,37,33,30],[39,33,32,36]], #Vmaf>80
              [[34,23,20,20], [32,33,28,27],[36,30,29,32]], #Vmaf>85
              [[26,18,15,15], [28,27,25,24],[31,25,24,30]], #Vmaf>90
              [[19,15,12,12], [19,18,19,19],[19,19,20,23]]] #Vmaf>95
        x=0
        for n in range(80,VMAF+1,5):x=x+1 
        return Vmaf[x-1][intra-1][inter-1]
        
    def PSNR(PSNR,intra,inter):
        # PSNR optimal QP
        Psnr=[[[42,35,35,35], [45,43,41,32],[45,43,40,34]], #PSNR>40
              [[40,22,21,21], [42,39,35,26],[42,36,34,34]], #PSNR>43
              [[34,19,18,18], [36,32,31,23],[37,26,25,31]], #PSNR>46
              [[29,18,16,15], [27,20,21,21],[26,20,19,19]]] #PSNR>49
        x=0
        for n in range(40,PSNR+1,3):x=x+1
        return Psnr[x-1][intra-1][inter-1]

