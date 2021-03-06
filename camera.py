import cv2
import threading,time,os
class RecordingThread (threading.Thread):
    def __init__(self, name, camera, identify):
        self.identify = identify
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True
        self.cap = camera
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))

    def run(self):
        counter = 1 ;
        while self.isRunning:
            ret, frame = self.cap.read()
            #if(self.identify==1):
            if(counter<=10):
                cv2.imwrite('image'+str(counter)+'.png',frame)
            #else :
                #cv2.imwrite('image'+str(counter)+'.png',frame)
            if(ret):
                self.out.write(frame)
            time.sleep(0.5)
            counter+=1;

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()

class VideoCamera(object):
    def __init__(self):
        # Open a camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 1)
      	
        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None
    
    def __del__(self):
        self.cap.release()
    
    def get_frame(self):
        print(self.cap.get(cv2.CAP_PROP_FPS))
        ret, frame = self.cap.read()

        frame = cv2.flip(frame,1)

        if ret:
            ret, jpeg = cv2.imencode('.jpg', frame)

            # Record video
            # if self.is_record:
            #     if self.out == None:
            #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            #         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))
                
            #     ret, frame = self.cap.read()
            #     if ret:
            #         self.out.write(frame)
            # else:
            #     if self.out != None:
            #         self.out.release()
            #         self.out = None  

            return jpeg.tobytes()
      
        else:
            return None

    def start_record(self,identify):
        self.is_record = True
        self.recordingThread = RecordingThread("Video Recording Thread", self.cap,identify)
        self.recordingThread.start()

    def stop_record(self,identify):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()
