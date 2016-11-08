'''
Compiling OpenCV2:
apt-get install build-essential
apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
apt-get install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

cd ~/opencv
mkdir release
cd release
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..

make
sudo make install

'''

'''
Tutorial:
https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html
http://docs.opencv.org/2.4/modules/contrib/doc/facerec/facerec_tutorial.html
http://docs.opencv.org/2.4/modules/contrib/doc/facerec/tutorial/facerec_video_recognition.html
http://docs.opencv.org/2.4/doc/user_guide/ug_traincascade.html
https://github.com/mbeyeler/opencv-python-bluyiannopouloseprints
http://memememememememe.me/post/training-haar-cascades/
http://hanzratech.in/2015/02/03/face-recognition-using-opencv.html     <------ this one is good
Template matching : http://docs.opencv.org/3.1.0/d4/dc6/tutorial_py_template_matching.html
'''

import os
import sys
import numpy as np
import cv2
#import cv2.cv as cv
from PIL import Image
import requests
import threading
import Queue
import time

print "#### OpenCV Version: " + cv2.__version__ + " ####"

# For face detection we will use the Haar Cascade provided by OpenCV.
cascade_path = "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

# For face recognition we will the the LBPH Face Recognizer
recognizer = cv2.createLBPHFaceRecognizer()#radius=2, neighbors=1, grid_x=2, grid_y=2)#, threshold=10.0)
#recognizer = cv2.createFisherFaceRecognizer()
#recognizer = cv2.createEigenFaceRecognizer()

VID_WIDTH = 400
VID_HEIGHT = 300
PROCESS_WIDTH = 200
PROCESS_HEIGHT = 150

POST_URL = "https://mixoff-analysis.eu-gb.mybluemix.net/test_upload"
#POST_URL = "https://mixoff-analysis.eu-gb.mybluemix.net/pic"
POST_TIMEOUT = 8

def Detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv.CV_HAAR_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def DrawRects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def GetImages(path, label, resize, trainImages, trainLabels):
    # Append all the absolute image paths in a list image_paths
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    # images will contains face images
    labels = []
    for image_path in image_paths:
        print "Processing : " + image_path

        # load the image - convert to grayscale
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        # equalize the image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))#equalizeHist(frame)
        image = clahe.apply(image)

        while True:
            # Detect the face in the image
            faces = face_cascade.detectMultiScale(image)

            if len(faces) is 0:
                print "No face found in image: " + image_path
                break
            else:
                print "    Found " + str(len(faces)) + " faces in image."

            # If face is detected, append the face to images 
            for (x, y, w, h) in faces:
                cropped_image = image[y: y + h, x: x + w]
                trainImages.append(cropped_image)
                trainLabels.append(label)
                splitpath, splitfilename = os.path.split(image_path)
                cv2.imwrite("temp/"+str(label)+"_"+str(x)+"_"+str(y)+"_"+splitfilename, cropped_image)
        
            if not resize:
                break

            print "    Resizing image..."
            image = cv2.resize(image, (0,0), fx=0.9, fy=0.9)

            # if image is smaller than threshold, then break out
            image_h, image_w = image.shape[:2]
            if image_h < 50 or image_w < 50:
                break


def TestFaceDetection():

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    img = cv2.imread('face.jpeg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    # perform actual detection - note there are additional params here that could be changed for our case
    faces = Detect(gray, face_cascade)
    #faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    vis = img.copy()
    DrawRects(img, faces, (255,0,0))

    #for x1, y1, x2, y2 in faces:
    #    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        #roi = gray[y1:y2, x1:x2]
        #vis_roi = vis[y1:y2, x1:x2]
        #subrects = detect(roi.copy())#, nested)
        #DrawRects(vis_roi, subrects, (255, 0, 0))

        #img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        #roi_gray = gray[y:y+h, x:x+w]
        #roi_color = img[y:y+h, x:x+w]
        #eyes = eye_cascade.detectMultiScale(roi_gray)
        #for (ex,ey,ew,eh) in eyes:
        #    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

    cv2.imshow('img',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def TestFaceRecognition():
        
    # load all the training images
    src_images = GetImages("faces/kevin_bacon/")

    # create labels
    labels = []
    for img in src_images:
        labels.append(0)

    # train the system with the images
    # since we are only training for 1 individual, the label will be 'zero'
    recognizer.train(src_images, np.array(labels))

    image_to_test = "IMG_20160928_161503.jpg"
    predict_image_pil = Image.open(image_to_test).convert('L')
    predict_image = np.array(predict_image_pil, 'uint8')
  
    print "About to perform recognition..." 
    # loop through all faces in the image
    faces = face_cascade.detectMultiScale(predict_image)
    for (x, y, w, h) in faces:
	nbr_predicted, conf = recognizer.predict(predict_image[y: y + h, x: x + w])
	#nbr_actual = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
	#if nbr_actual == nbr_predicted:
	#    print "{} is Correctly Recognized with confidence {}".format(nbr_actual, conf)
	#else:
	#    print "{} is Incorrect Recognized as {}".format(nbr_actual, nbr_predicted)
        print "nbr_predicted = " + str(nbr_predicted)
        print "conf (closer to zero is better match) = " + str(conf)
	cv2.imshow("Recognizing Face", predict_image[y: y + h, x: x + w])
	cv2.waitKey(0)

    #faceRecognizer = cv2.FaceRecognizer()
    #print faceRecognizer

################################################################################################

class PostingThread(threading.Thread):
    def __init__(self, filename, url, queue):
        super(PostingThread, self).__init__()
        self.filename = filename
        self.url = url
        self.queue = queue
        self.queue.put(1) # put 1 to signify we are running thread

    def run(self):
        headers = {'Content-Type': 'image/jpeg'}
        try:
            data = open(self.filename, 'rb').read()
            r = requests.post(self.url, headers=headers, data=data, timeout=POST_TIMEOUT)
            #print(r.text)
        except Exception as e:
            print str(e)
            
        self.queue.get() # pop 1 to signify we have finished thread

def Run(inputSrc):
    # can use ffmpeg to encode video from source into a FIFO:
    # ffmpeg -f v4l2 -framerate 25 -video_size 640x480 -input_format mjpeg -i /dev/video0 output.mkv
    # Fifo:
    # mkfifo arsdk_fifo
    # ffmpeg -f v4l2 -framerate 25 -video_size 640x480 -input_format mjpeg -i /dev/video0 pipe:1 > arsdk_fifo

    print "Waiting for live feed..."
    #cap = cv2.VideoCapture(r"/tmp/arsdk_ByirST/arsdk_fifo")
    cap = cv2.VideoCapture(inputSrc)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, VID_WIDTH)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, VID_HEIGHT)

    if not cap.isOpened(): 
	print 'Cannot initialize video capture'
	return

    font = cv2.FONT_HERSHEY_SIMPLEX

    resize = True
    screenshotQueue = Queue.Queue()
    post = False

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        if resize:
            frame = cv2.resize(frame, (PROCESS_WIDTH,PROCESS_HEIGHT))

        # convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) 
        # equalize the image
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))#equalizeHist(frame)
        gray = clahe.apply(gray)

        # loop through all faces in the image
        faces = face_cascade.detectMultiScale(gray)
        print "Faces detected = " + str(len(faces))
        for (x, y, w, h) in faces:
            nbr_predicted, conf = recognizer.predict(gray[y:y+h, x:x+w])
            #print "    nbr_predicted = " + str(nbr_predicted)
            #print "    conf (closer to zero is better match) = " + str(conf)
            col = (255,0,0)

            #if conf < 0.1 and nbr_predicted == 0:
            if nbr_predicted == 0:
                col = (0,0,255)
                post = True

                #imgToPost = frame.copy()
                #roi = frame[y:(y+h), x:(x+w)]
                #cv2.imshow("Cropped", roi)
                #cv2.imwrite("/tmp/cropped.jpg", roi)
                #cv2.waitKey(5)

            cv2.rectangle(frame, (x, y), (x+w, y+h), col, 1)
            #cv2.putText(frame,str(nbr_predicted) + " : " + str(conf),(x+5,y-15), font, 0.5,(255,0,0),1)#,cv2.LINE_AA)
            cv2.putText(frame,str(nbr_predicted),(x+5,y-15), font, 0.5,(255,0,0),1)#,cv2.LINE_AA)

        if resize:
            frame = cv2.resize(frame, (VID_WIDTH,VID_HEIGHT))
        
        frame = cv2.resize(frame, (1280,720))

        cv2.imshow("Recognizing Face", frame)

        if post and screenshotQueue.empty():
            print "Posting image..."
            # write file to disk
            tmpJPG = "/tmp/tmp.jpg"
            cv2.imwrite(tmpJPG, frame)
            # upload the image in a new thread
            postingThread = PostingThread(tmpJPG, POST_URL, screenshotQueue)
            postingThread.start()
            post = False

        key = cv2.waitKey(1)
        c = chr(key & 255)
        
        if c in ['q', 'Q', chr(27)]:
            break

    cap.release()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage : python server.py 'VidInputSource'"
        print ""
        print "VidInputSource can be 0 or a file or FIFO."
        exit(1)

    inputSrc = sys.argv[1]
    try:
        # try converting the input source to an int
        # we leave it as a string if this fails
        i = int(inputSrc)
        inputSrc = i
    except Exception as e:
        pass

    # train the system with the images
    print "Training..."

    trainImages = []
    trainLabels = []
    # train the recognizer with "false" data
    GetImages("trainingdata_target/", 0, True, trainImages, trainLabels)
    GetImages('trainingdata_tomcruise/', 1, True, trainImages, trainLabels)
    GetImages('trainingdata_judy/', 2, True, trainImages, trainLabels)
    GetImages('trainingdata_scarlett/', 3, True, trainImages, trainLabels)
    GetImages('trainingdata_false/', 4, False, trainImages, trainLabels)

    print trainLabels

    recognizer.train(trainImages, np.array(trainLabels))
   
    Run(inputSrc)


