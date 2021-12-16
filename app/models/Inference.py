
from flask import flash
from app.monitor.src.tf_model_object_detection import Model
from app.models.Occurrence import Occurrence
from app.models.alchemy_encoder import AlchemyEncoder
import cv2
import numpy as np
from app import socketio, db 
import datetime;
import imutils
from app.monitor.src.bird_view_transfo_functions import compute_perspective_transform,compute_point_perspective_transformation
import itertools
import math

class Inference():
    def __init__(self, config_id, width_og, height_og, size_frame, points, capacity, camera_address, minimum_distance):
        self.config_id = config_id
        self.corner_points = points
        self.width_og = width_og
        self.height_og = height_og
        self.size_frame = size_frame
        self.img_path = 'app/monitor/img/static_frame_from_video.jpg'
        self.camera_address = camera_address
        #self.model = YoloModel('app/monitor/models/yolov3-tiny.weights')
        self.model = Model('app/monitor/models/yolov4-tiny-416.tflite')
        #self.model = Model('app/monitor/models/ssdlite_object_detection')

        #self.model = HogModel()
        self.minumun_distance = minimum_distance
        self.capacity = capacity
        self.current_capacity = 0
        self.COLOR_RED = (0, 0, 255)
        self.COLOR_GREEN = (0, 255, 0)
        self.COLOR_BLUE = (255, 0, 0)
        self.BIG_CIRCLE = 60
        self.SMALL_CIRCLE = 3
        self.idxs_occ = []

    
    def register_occurrency(self, type):
        occurrence = Occurrence(type, self.current_capacity, self.config_id)
        db.session.add(occurrence)
        db.session.commit()

    def triggerAlertDistancing(self, idxs1, idxs2):
        if not idxs1 in self.idxs_occ or not idxs2 in self.idxs_occ:
            self.idxs_occ += [idxs1, idxs2]
            self.register_occurrency('distânciamento')
        

    def init(self):

        matrix,imgOutput = compute_perspective_transform(self.corner_points,self.width_og,self.height_og, cv2.imread(self.img_path))
        height,width,_ = imgOutput.shape

 
        blank_image = np.zeros((height,width,3), np.uint8)
        height = blank_image.shape[0]
        width = blank_image.shape[1] 
        dim = (width, height)

        video_source = None
        try:
            video_source = int(self.camera_address)
        except ValueError:
            video_source = self.camera_address
        vs = cv2.VideoCapture(video_source)
        socketio.emit('alert-distance', {'status': 'success', 'message': 'Nenhuma ocorrência detectada'})
        socketio.emit('alert-capacity', {'status': 'success', 'message': 'Lotação de pessoas não antigiu a capacidade máxima.'})



        output_video_1,output_video_2 = None,None
        # Loop until the end of the video stream
        while True:	
            # Load the image of the ground and resize it to the correct size
            bird_view_img = np.zeros((height, width, 3), np.uint8)

            #bird_view_img = cv2.resize(blank_image, dim, interpolation = cv2.INTER_AREA)

      
            # Load the frame
            (frame_exists, frame) = vs.read()

        
            # Test if it has reached the end of the video
            if not frame_exists:
                flash('Transmissão encerreda externamente', 'warning')
                break
            else:
                # Resize the image to the correct size
                frame = imutils.resize(frame, width=int(self.size_frame))
                # Make the predictions for this frame
                (boxes, scores, classes, idxs) = self.model.model_inference(frame)

                # Get the human detected in the frame and return the 2 points to build the bounding box  
                array_boxes_detected = self.get_human_box_detection(boxes,scores,classes,frame.shape[0],frame.shape[1])
                
                # Both of our lists that will contain the centroïds coordonates and the ground points
                array_centroids,array_groundpoints = self.get_centroids_and_groundpoints(array_boxes_detected)

                # Use the transform matrix to get the transformed coordonates
                transformed_downoids = compute_point_perspective_transformation(matrix,array_groundpoints)
                
                # Show every point on the top view image 
                for i, point in enumerate(transformed_downoids):
                    x,y = point
                    cv2.circle(bird_view_img, (int(x),int(y)), self.BIG_CIRCLE, self.COLOR_GREEN, 2)
                    cv2.circle(bird_view_img, (int(x),int(y)), self.SMALL_CIRCLE, self.COLOR_GREEN, -1)
                    cv2.putText(bird_view_img, str(idxs[i]),((int(x),int(y)-10)),0, 0.75, (255,255,255),2)


                # Check if 2 or more people have been detected (otherwise no need to detect)
                socketio.emit('update_status', {'num_peoples':len(transformed_downoids)})
                if len(transformed_downoids) > self.capacity:
                    socketio.emit('alert-capacity', {'status': 'danger', 'message': f'Lotação máxima ultrapasada em {len(transformed_downoids) - self.capacity} pessoas!'})
                    if self.current_capacity != len(transformed_downoids):
                        self.register_occurrency('lotação')
                else:
                    socketio.emit('alert-capacity', {'status': 'success', 'message': 'Lotação de pessoas não antigiu a capacidade máxima.'})
                self.current_capacity = len(transformed_downoids)

                if len(transformed_downoids) >= 2:
                    for index,downoid in enumerate(transformed_downoids):
                        if not (downoid[0] > width or downoid[0] < 0 or downoid[1] > height+200 or downoid[1] < 0 ):
                            cv2.rectangle(frame,(array_boxes_detected[index][1],array_boxes_detected[index][0]),(array_boxes_detected[index][3],array_boxes_detected[index][2]),self.COLOR_GREEN,2)
                            cv2.putText(frame, str(idxs[index]),(array_boxes_detected[index][1], array_boxes_detected[index][0]-10),0, 0.75, (255,255,255),2)

                   
                    # Iterate over every possible 2 by 2 between the points combinations 
                    list_indexes = list(itertools.combinations(range(len(transformed_downoids)), 2))
                    for i,pair in enumerate(itertools.combinations(transformed_downoids, r=2)):
                        # Check if the distance between each combination of points is less than the minimum distance chosen
                        if math.sqrt( (pair[0][0] - pair[1][0])**2 + (pair[0][1] - pair[1][1])**2 ) < int(100):
                            # Change the colors of the points that are too close from each other to red
                            if not (pair[0][0] > width or pair[0][0] < 0 or pair[0][1] > height+200  or pair[0][1] < 0 or pair[1][0] > width or pair[1][0] < 0 or pair[1][1] > height+200  or pair[1][1] < 0):
                                cv2.circle(bird_view_img, (int(pair[0][0]),int(pair[0][1])), self.BIG_CIRCLE, self.COLOR_RED, 2)
                                cv2.circle(bird_view_img, (int(pair[0][0]),int(pair[0][1])), self.SMALL_CIRCLE, self.COLOR_RED, -1)
                                cv2.circle(bird_view_img, (int(pair[1][0]),int(pair[1][1])), self.BIG_CIRCLE, self.COLOR_RED, 2)
                                cv2.circle(bird_view_img, (int(pair[1][0]),int(pair[1][1])), self.SMALL_CIRCLE, self.COLOR_RED, -1)
                                # Get the equivalent indexes of these points in the original frame and change the color to red
                                #self.register_occurrency('distânciamento')

                                index_pt1 = list_indexes[i][0]
                                index_pt2 = list_indexes[i][1]
                                cv2.rectangle(frame,(array_boxes_detected[index_pt1][1],array_boxes_detected[index_pt1][0]),(array_boxes_detected[index_pt1][3],array_boxes_detected[index_pt1][2]),self.COLOR_RED,2)
                                cv2.rectangle(frame,(array_boxes_detected[index_pt2][1],array_boxes_detected[index_pt2][0]),(array_boxes_detected[index_pt2][3],array_boxes_detected[index_pt2][2]),self.COLOR_RED,2)
                                self.triggerAlertDistancing(index_pt1, idxs[index_pt2])
                                socketio.emit('alert-distance', {'status': 'danger', 'message': 'Distânciamento social desrespeitado'})
                            else:
                                socketio.emit('alert-distance', {'status': 'success', 'message': 'Nenhuma ocorrência detectada'})
                self.draw_rectangle(frame)
                cv2.putText(frame, 'Vista normal',(10,30),fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, color=(255,255,255),fontScale=1)
                cv2.putText(bird_view_img, 'Vista em perspectiva',(10,30),fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, color=(255,255,255),fontScale=1)

                bird_view_img = imutils.resize(bird_view_img, width=int(self.size_frame))
                added_image = cv2.hconcat([frame, bird_view_img])
                #added_image = np.concatenate((frame, bird_view_img), axis=1)

                ret, buffer = cv2.imencode('.jpg', added_image)
                bframe = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + bframe + b'\r\n')

    def get_human_box_detection(self, boxes,scores,classes,height,width):
        """ 
        For each object detected, check if it is a human and if the confidence >> our threshold.
        Return 2 coordonates necessary to build the box.
        @ boxes : all our boxes coordinates
        @ scores : confidence score on how good the prediction is -> between 0 & 1
        @ classes : the class of the detected object ( 1 for human )
        @ height : of the image -> to get the real pixel value
        @ width : of the image -> to get the real pixel value
        """
        # array_boxes = list() # Create an empty list
        # for i in range(len(scores)):
           
        #     #If the class of   the detected object is 1 and the confidence of the prediction is > 0.6
        #     if classes[i] == 0 and scores[i] > 0.5:
        #         # To transform the box value into pixel coordonate values.
        #         #box = [boxes[0,i,0],boxes[0,i,1],boxes[0,i,2],boxes[0,i,3]] * np.array([height, width, height, width])
        #         # Add the results converted to int
        #         # ymin = int(max(1,(boxes[i][0] * height)))
        #         # xmin = int(max(1,(boxes[i][1] * width)))
        #         # ymax = int(min(height,(boxes[i][2] * height)))
        #         # xmax = int(min(width,(boxes[i][3] * width)))

        #         ymin = int(max(1,(boxes[i][0] )))
        #         xmin = int(max(1,(boxes[i][1] )))
        #         ymax = int(min(height,(boxes[i][2] )))
        #         xmax = int(min(width,(boxes[i][3])))
        #         array_boxes.append((int(ymin),int(xmin),int(ymax),int(xmax)))
        #         #pass

        # for track in tracker.tracks:
        #     if not track.is_confirmed() or track.time_since_update > 1:
        #         continue 
        #     bbox = track.to_tlbr()
        #     class_name = track.get_class()
        #     array_boxes.append((int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])))
        #print(tracker.tracks)
        return boxes


    def get_centroids_and_groundpoints(self, array_boxes_detected):
        """
        For every bounding box, compute the centroid and the point located on the bottom center of the box
        @ array_boxes_detected : list containing all our bounding boxes 
        """
        array_centroids,array_groundpoints = [],[] # Initialize empty centroid and ground point lists 
        for index,box in enumerate(array_boxes_detected):
            # Draw the bounding box 
            # c
            # Get the both important points
            centroid,ground_point = self.get_points_from_box(box)
            array_centroids.append(centroid)
            array_groundpoints.append(centroid)
        return array_centroids,array_groundpoints


    def get_points_from_box(self, box):
        """
        Get the center of the bounding and the point "on the ground"
        @ param = box : 2 points representing the bounding box
        @ return = centroid (x1,y1) and ground point (x2,y2)
        """
        # Center of the box x = (x1+x2)/2 et y = (y1+y2)/2
        center_x = int(((box[1]+box[3])/2))
        center_y = int(((box[0]+box[2])/2))
        # Coordiniate on the point at the bottom center of the box
        center_y_ground = center_y + ((box[2] - box[0])/2)
        return (center_x,center_y),(center_x,int(center_y_ground))
        

    def draw_rectangle(self, frame):
        # Draw rectangle box over the delimitation area
        cv2.line(frame, (self.corner_points[1][0], self.corner_points[1][1]), (self.corner_points[3][0], self.corner_points[3][1]), self.COLOR_BLUE, thickness=1)
        cv2.line(frame, (self.corner_points[3][0], self.corner_points[3][1]), (self.corner_points[2][0], self.corner_points[2][1]), self.COLOR_BLUE, thickness=1)
        cv2.line(frame, (self.corner_points[2][0], self.corner_points[2][1]), (self.corner_points[0][0], self.corner_points[0][1]), self.COLOR_BLUE, thickness=1)
        cv2.line(frame, (self.corner_points[0][0], self.corner_points[0][1]), (self.corner_points[1][0], self.corner_points[1][1]), self.COLOR_BLUE, thickness=1)