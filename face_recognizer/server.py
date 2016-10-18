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

Instaling CherryPy
apt-get install python-pip
apt-get install python-setuptools
pip install CherryPy
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
#import cherrypy

print "#### OpenCV Version: " + cv2.__version__ + " ####"

# For face detection we will use the Haar Cascade provided by OpenCV.
cascade_path = "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

# For face recognition we will the the LBPH Face Recognizer
recognizer = cv2.createLBPHFaceRecognizer(radius=2, neighbors=1, grid_x=2, grid_y=2)#, threshold=10.0)
#recognizer = cv2.createFisherFaceRecognizer()
#recognizer = cv2.createEigenFaceRecognizer()

def Detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv.CV_HAAR_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def DrawRects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

def GetImages(path, label, resize=False):
    # Append all the absolute image paths in a list image_paths
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    # images will contains face images
    images = []
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
                images.append(cropped_image)
                labels.append(label)
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

    # return the images list
    return images, labels


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


def Run():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 240)

    window_name = "Video capture"

    if not cap.isOpened(): 
	print 'Cannot initialize video capture'
	sys.exit(-1)

    font = cv2.FONT_HERSHEY_SIMPLEX

    frame_number = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

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
            print "    nbr_predicted = " + str(nbr_predicted)
            print "    conf (closer to zero is better match) = " + str(conf)
            col = (255,0,0)

            if conf < 0.02 and nbr_predicted == 0:
                col = (0,0,255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), col, 2)
            cv2.putText(frame,str(nbr_predicted) + " : " + str(conf),(x+5,y-15), font, 0.5,(255,0,0),2)#,cv2.LINE_AA)

        #frame = cv2.resize(frame, (0,0), fx=3.0, fy=3.0)
        cv2.imshow("Recognizing Face", frame)
        key = cv2.waitKey(1)
        c = chr(key & 255)
        if c in ['q', 'Q', chr(27)]:
            break
        frame_number += 1

    cap.release()


if __name__ == '__main__':
    #TestFaceRecognition()
    #TestFaceDetection()

    images_target, labels_target = GetImages("trainingdata_target/", 0, True)
    images_false, labels_false = GetImages('trainingdata_false/', 1)

    # train the system with the images
    print "Training..."
    recognizer.train(images_target+images_false, 
            np.array(labels_target+labels_false))
    print "Training completed."
    
    Run()
    #exit()
    #cap = cv2.VideoCapture(0)

    #conf = {
    #    '/': {
    #        'tools.sessions.on': True,
    #        'tools.staticdir.root': os.path.abspath(os.getcwd())
    #    },
    #    '/static': {
    #        'tools.staticdir.on': True,
    #        'tools.staticdir.dir': './public'
    #    }
    #}
    #cherrypy.quickstart(StringGenerator(), '/', conf)


