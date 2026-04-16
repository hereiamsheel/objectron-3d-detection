import cv2
import mediapipe as mp
import os
import time
import datetime

mp_objectron = mp.solutions.objectron
mp_drawing = mp.solutions.drawing_utils

# Create output folder
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

# Create timestamp filename
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"result_{timestamp}.mp4"

# MP4 Video Writer
fourcc = cv2.VideoWriter_fourcc(*'avc1')
out = cv2.VideoWriter(os.path.join(output_dir, filename),
                      fourcc,
                      20.0,
                      (640, 480))

cap = cv2.VideoCapture('../test-resources/cup.mp4')
cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Webcam", 640, 480)

with mp_objectron.Objectron(static_image_mode = False,
                            max_num_objects = 2,
                            min_detection_confidence = 0.4,
                            min_tracking_confidence = 0.4,
                            model_name = 'Cup') as objectron:
    
    while cap.isOpened():
        success, image = cap.read()
        start = time.time()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.flip(image,1)
        image = cv2.resize(image, (640, 480))
        # Convert the BGR iamge to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # To improve performance, optionally mark the image as not writable to
        # pass by reference .
        image.flags.writeable = False
        results = objectron.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.detected_objects:
            for detected_object in results.detected_objects:
                mp_drawing.draw_landmarks(image, detected_object.landmarks_2d, mp_objectron.BOX_CONNECTIONS)
                mp_drawing.draw_axis(image, detected_object.rotation, detected_object.translation)

        # FPS calculation 
        end = time.time()
        totalTime = end - start
        fps = 1 / totalTime

        cv2.putText(image, f'FPS : {int(fps)}', 
                    (20,70), 
                    cv2.FONT_HERSHEY_PLAIN, 
                    1, 
                    (40,255,40),
                    2)

        cv2.imshow("WebCam", image)
        out.write(image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()  
cv2.destroyAllWindows()