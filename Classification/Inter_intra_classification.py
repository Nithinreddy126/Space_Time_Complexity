import yuvio # pip install yuvio
import numpy as np 

class intra_inter_classification :

    def __init__(self,filename,dims,yuvformat,startFrame,nframes):
        #variable declaration
        self.filename=filename
        self.width=dims[0]
        self.height=dims[1]
        self.yuvformat=yuvformat
        self.startFrame=startFrame
        self.nframes=nframes
        self.variancefY,self.variancefU,self.variancefV,self.midfY=[],[],[],[]
        self.midfU,self.midfV,self.Ymid,self.vYIntra =[],[],[],[]
        self.vYIntra,self.Ym,self.Ydiff=0,0,0
        self.yuv_frames=[]
        
        
    def get_intra_inter(self,m):
        # itiration for each frame 
        for i in range(self.startFrame,self.startFrame+self.nframes):
            self.intra_calculation(i)#intra calculations
              
            if i< self.nframes+self.startFrame-30:self.inter_calculation(i)# call inter calculations
            #call clear_ variables to delete created arrays
            self.clear_varibles()
            
        if self.nframes>=30: inter=self.inter_class() #get inter classification
        intra=self.intra_class()#get intra classification
        return [intra, inter]

    def intra_calculation(self,i):
        # read the frame of yuv video 
        self.yuv_frames = yuvio.mimread(self.filename, self.width, self.height, self.yuvformat,i,1)
    
        #luminance part- find variance of the y frame
        self.midfY.append(np.mean(self.yuv_frames[0].y))
        self.variancefY.append(np.var(self.yuv_frames[0].y))
        
        #Chrominance U part- find variance of U frame
        # self.midfU.append(np.mean(self.yuv_frames[0].u))
        # self.variancefU.append(np.var(self.yuv_frames[0].u))

        #Chrominance V part- find variance of V frame
        # self.midfV.append(np.mean(self.yuv_frames[0].v))
        # self.variancefV.append(np.var(self.yuv_frames[0].v))
        
        # add variance of each frame to variable
        self.vYIntra=self.vYIntra+int((np.mean(self.variancefY[0])))
        
        


    def inter_calculation(self,n):
        # read 31st frame( Reference Frame) of yuv video
        yuv_frame_temp =yuvio.mimread(self.filename, self.width, self.height, self.yuvformat, n+30,1)
        # difference of current frame refrence frame
        self.Ydiff=np.mean(np.abs(np.subtract(self.yuv_frames[0].y.astype(np.int64),yuv_frame_temp[0].y.astype(np.int64))))
        # add diffrence to variable
        self.Ym=self.Ym+int(self.Ydiff)
        
        

    def intra_class(self):
        #classify Intra
        avg_intra=int(self.vYIntra/self.nframes) 
        
        if(0 <= avg_intra & avg_intra <= 10000):intra = 1
        elif(10000 < avg_intra & avg_intra <= 40000):intra = 2
        elif(avg_intra > 40000):intra = 3
        return intra

    def inter_class(self):
        #Classify Inter
        avg_Ym=int(np.divide(self.Ym,self.nframes-30))
    
        if(0 <= avg_Ym & avg_Ym <= 50): inter = 1
        elif(50 < avg_Ym & avg_Ym <= 80):inter = 2
        elif(80 < avg_Ym & avg_Ym <= 105):inter = 3
        elif(avg_Ym > 105):inter = 4
            
        return inter
        

    def clear_varibles(self):
        #clear variables
        self.variancefY.clear()
        self.midfU.clear()
        self.variancefU.clear()
        self.midfY.clear()
        self.midfV.clear()
        self.variancefV.clear()
        self.yuv_frames.clear()
        


# if __name__ == "__main__":
#     filename="input.yuv"
#     dims=[3840, 2160]
#     yuvformat='yuv420p10le'
#     startFrame=0
#     nframes=400
#     classification=intra_inter_classification(filename,dims,yuvformat,startFrame,nframes)
#     intra=classification.get_intra_inter(1)
#     if nframes<=30: print(f'intra: {intra[0]} \'interUnattainable for fewer than 31 frames')
#     else: print(f'intra: {intra[0]} inter: {intra[1]}')