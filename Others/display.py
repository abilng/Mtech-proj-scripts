#!/usr/bin/env python2.7
import numpy as np
import cv2

def draw_str(dst, (x, y), s):
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.CV_AA)

def playVideo(videofile,labels,labeltitle,outFile=None):
    cap = cv2.VideoCapture(videofile)
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES,0)
    fps = int(cap.get(cv2.cv.CV_CAP_PROP_FPS));
    N = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    heigth = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    print("No of Frames        : "+ str(N));
    print("Original Width      : " +str(width)); 
    print("Original Height     : " +str(heigth));
    print("Original FrameRate  : " +str(fps));
    i=0;
    save = not(outFile==None);
    if save:
        video_writer = cv2.VideoWriter(outFile,cv2.cv.CV_FOURCC(*'MJPG'),fps, (width, heigth))

    while True:
        ret, img = cap.read()
        print 'Playing/Saving ....................... [{0}%]\r'.format((i*100/N)),
        if not ret:
            break

        draw_str(img, (20, 20), labeltitle +" : " + labels[i])
        if save:
            video_writer.write(img)
        else:
            cv2.imshow('video', img)
            ch = 0xFF & cv2.waitKey(1000/(fps+1))
            if ch == ord('q') or ch == 27:
                break
        i+=1

    if save:
    	video_writer.release()
    cap.release()
    print('Playing/Saving ....................... [DONE]')
    cv2.destroyAllWindows()



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('videoFile')
    parser.add_argument('labelFile')
    parser.add_argument('labels',nargs='+',help='labels(string) in order')
    parser.add_argument('--save',dest='outFile',default=None,help="Saving to outFile")
    args = parser.parse_args()
    
    print args

    #labelNames=["boxing","clapping","waving"]
    #labelNames=["Passing","Catching","HoldingBall","Jumping","Dribbling"]
    labelNames=args.labels;
    print 'labels are :',labelNames
    fileptr = open(args.labelFile,'r');
    lab =[ int(x[0]) for x in fileptr.readlines() ]
    labels = [labelNames[l] for l in lab ]
    playVideo(args.videoFile,labels,'label',args.outFile)
