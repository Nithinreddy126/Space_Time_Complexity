from tkinter.filedialog import askopenfilename
import Classification.Scene_detect as sd
import time


if __name__ == "__main__":
    filetypes = (('All files', '*.mxf'),('All files', '*.mp4'),('All files', '*.mov'))
    filename = askopenfilename(filetypes=filetypes)#input video file in mxf or mp4
    #input YUV format,deisired Vmaf and PSNR
    yuvformat=str(input('Enter the desired pixel format and bitdepth(ex. yuv420p8le, yuv420p10le): '))
    VideoSplit = str(input('Do you want to save the raw YUV files of separated scenes[Y/N]: '))
    Vmaf=int(input('Enter the desired value of Vmaf (95,90,85,80): '))
    Psnr=int(input('Enter the desired value of Psnr (49,46,43,40): '))
    print(f'------------------------------------------------------------')
    start=time.time()
    while(True):
        if VideoSplit.upper() == 'Y' or VideoSplit.upper() =='N':
            print('Getting scene list........')
            Scene = sd.SceneDetect(filename,yuvformat,Psnr,Vmaf)
            results=Scene.threads_idx(VideoSplit.upper())
            result=results[0]
            nScene=results[1]
            scene_list=results[2]
            print(f'scenes-------{nScene}')
            #print results
            for j in range(nScene):
                print(f'--------------------------------')
                print(f'scnene no--{result[j][0]}')
                print(scene_list[j])
                print(f'intra:{int(result[j][2])}    inter{int(result[j][3])}')
                print(f'QP<={int(result[j][4])} for Vmaf: {Vmaf}   ||    QP<={int(result[j][5])} for PSNR: {Psnr}')
            print(f'Total time of execution: {int(time.time()-start)} secs') #Substract start time and end time
            break
        else:
            VideoSplit = str(input('Choose only Y/N :'))
    