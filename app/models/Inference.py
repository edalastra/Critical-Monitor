from app.monitor.src.tf_model_object_detection import Model 
from app.monitor.src.social_distanciation_video_detection import *
import cv2
import numpy as np
from app import socketio

class Inference():
    def __init__(self, width_og, height_og, size_frame, points):
        self.corner_points = points
        self.width_og = width_og
        self.height_og = height_og
        self.size_frame = size_frame
        self.img_path = 'app/monitor/img/static_frame_from_video.jpg'
        self.model = Model('app/monitor/models/ssdlite_mobiledet_cpu_320x320_coco_2020_05_19/model.tflite')
        self.distance_minimum = "2"
    
    def init(self):
        matrix,imgOutput = compute_perspective_transform(self.corner_points,self.width_og,self.height_og, cv2.imread(self.img_path))
        height,width,_ = imgOutput.shape
        blank_image = np.zeros((height,width,3), np.uint8)
        height = blank_image.shape[0]
        width = blank_image.shape[1] 
        dim = (width, height)
        vs = cv2.VideoCapture("app/monitor/video/PETS2009.avi")
        output_video_1,output_video_2 = None,None
        # Loop until the end of the video stream
        while True:	
            # Load the image of the ground and resize it to the correct size
            img = cv2.imread("app/monitor/img/chemin_1.png")
            bird_view_img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            
            # Load the frame
            (frame_exists, frame) = vs.read()
            # Test if it has reached the end of the video
            if not frame_exists:
                break
            else:
                # Resize the image to the correct size
                #frame = imutils.resize(frame, width=int(size_frame))
                
                # Make the predictions for this frame
                (boxes, scores, classes) = self.model.predict(frame)

                # Get the human detected in the frame and return the 2 points to build the bounding box  
                array_boxes_detected = get_human_box_detection(boxes,scores,classes,frame.shape[0],frame.shape[1])
                
                # Both of our lists that will contain the centroïds coordonates and the ground points
                array_centroids,array_groundpoints = get_centroids_and_groundpoints(array_boxes_detected)

                # Use the transform matrix to get the transformed coordonates
                transformed_downoids = compute_point_perspective_transformation(matrix,array_groundpoints)
                
                # Show every point on the top view image 
                for point in transformed_downoids:
                    x,y = point
                    cv2.circle(bird_view_img, (int(x),int(y)), BIG_CIRCLE, COLOR_GREEN, 2)
                    cv2.circle(bird_view_img, (int(x),int(y)), SMALL_CIRCLE, COLOR_GREEN, -1)

                # Check if 2 or more people have been detected (otherwise no need to detect)
                socketio.emit('update_status', {'num_peoples':len(transformed_downoids)})

                if len(transformed_downoids) >= 2:
                    for index,downoid in enumerate(transformed_downoids):
                        if not (downoid[0] > width or downoid[0] < 0 or downoid[1] > height+200 or downoid[1] < 0 ):
                            cv2.rectangle(frame,(array_boxes_detected[index][1],array_boxes_detected[index][0]),(array_boxes_detected[index][3],array_boxes_detected[index][2]),COLOR_GREEN,2)

                    # Iterate over every possible 2 by 2 between the points combinations 
                    list_indexes = list(itertools.combinations(range(len(transformed_downoids)), 2))
                    for i,pair in enumerate(itertools.combinations(transformed_downoids, r=2)):
                        # Check if the distance between each combination of points is less than the minimum distance chosen
                        if math.sqrt( (pair[0][0] - pair[1][0])**2 + (pair[0][1] - pair[1][1])**2 ) < int(100):
                            # Change the colors of the points that are too close from each other to red
                            if not (pair[0][0] > width or pair[0][0] < 0 or pair[0][1] > height+200  or pair[0][1] < 0 or pair[1][0] > width or pair[1][0] < 0 or pair[1][1] > height+200  or pair[1][1] < 0):
                                #change_color_on_topview(pair)
                                # Get the equivalent indexes of these points in the original frame and change the color to red
                                
                                index_pt1 = list_indexes[i][0]
                                index_pt2 = list_indexes[i][1]
                                cv2.rectangle(frame,(array_boxes_detected[index_pt1][1],array_boxes_detected[index_pt1][0]),(array_boxes_detected[index_pt1][3],array_boxes_detected[index_pt1][2]),COLOR_RED,2)
                                cv2.rectangle(frame,(array_boxes_detected[index_pt2][1],array_boxes_detected[index_pt2][0]),(array_boxes_detected[index_pt2][3],array_boxes_detected[index_pt2][2]),COLOR_RED,2)

                ret, buffer = cv2.imencode('.jpg', frame)
                bframe = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + bframe + b'\r\n')

