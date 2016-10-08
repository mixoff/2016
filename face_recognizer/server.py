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

'''

import os
import sys
import numpy as np
import cv2
#import cv2.cv as cv
from PIL import Image

print "#### OpenCV Version: " + cv2.__version__ + " ####"

# For face detection we will use the Haar Cascade provided by OpenCV.
cascade_path = "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

# For face recognition we will the the LBPH Face Recognizer
recognizer = cv2.createLBPHFaceRecognizer()

def Detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv.CV_HAAR_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def DrawRects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def GetImages(path):
    # Append all the absolute image paths in a list image_paths
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    # images will contains face images
    images = []
    for image_path in image_paths:
        print "Processing : " + image_path
        # Read the image and convert to grayscale
        image_pil = Image.open(image_path).convert('L')
        # Convert the image format into numpy array
        image = np.array(image_pil, 'uint8')
        # Detect the face in the image
        faces = face_cascade.detectMultiScale(image)

        if len(faces) is 0:
            print "No face found in image: " + image_path
        else:
            print "    Found " + str(len(faces)) + " faces in image."

        # If face is detected, append the face to images 
        for (x, y, w, h) in faces:
            images.append(image[y: y + h, x: x + w])
    # return the images list
    return images


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

def TestVideo():
    cap = cv2.VideoCapture(0)
    #cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
    #cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

    window_name = "Data Matrix Detector"

    if not cap.isOpened(): 
	print 'Cannot initialize video capture'
	sys.exit(-1)                           

    frame_number = 0

    while True:
        ret, frame = cap.read()
        print str(frame)

        if not ret:
            break

	gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY) 
	codes, corners, dmtx = cv2.findDataMatrix(gray)

	cv2.drawDataMatrixCodes(frame, codes, corners) 
	cv2.imshow(window_name, frame)                 

        key = cv2.waitKey(30)
        c = chr(key & 255)
        if c in ['q', 'Q', chr(27)]:
            break
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # etc...
        frame_number += 1

    #cap.release()

def data_matrix_demo(cap):                                   
    window_name = "Data Matrix Detector"                     
    frame_number = 0
    need_to_save = False
    
    while 1: 
        ret, frame = cap.read()                              
        if not ret:                                          
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)       
        codes, corners, dmtx = cv2.findDataMatrix(gray)      
    
        cv2.drawDataMatrixCodes(frame, codes, corners)       
        cv2.imshow(window_name, frame)                       
            
        key = cv2.waitKey(30)
        c = chr(key & 255)
        if c in ['q', 'Q', chr(27)]:
            break
        
        if c == ' ':
            need_to_save = True                              
                                                             
        if need_to_save and codes:                           
            filename = ("datamatrix%03d.jpg" % frame_number) 
            cv2.imwrite(filename, frame)                     
            print "Saved frame to " + filename               
            need_to_save = False                             
                                                             
        frame_number += 1
    


#TestFaceRecognition()
#TestFaceDetection()
TestVideo()
#cap = cv2.VideoCapture(0)
#data_matrix_demo(cap)


