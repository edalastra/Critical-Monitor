from .bird_view_transfo_functions import compute_perspective_transform,compute_point_perspective_transformation
from .tf_model_object_detection import Model 
from .colors import bcolors
import numpy as np
import itertools
import imutils
import time
import math
import glob
import yaml
import cv2
import os







######################################### 
# Load the config for the top-down view #
#########################################
# print(bcolors.WARNING +"[ Loading config file for the bird view transformation ] "+ bcolors.ENDC)
# with open("app/monitor/conf/config_birdview.yml", "r") as ymlfile:
#     cfg = yaml.load(ymlfile)
# width_og, height_og = 0,0
# corner_points = []

# for section in cfg:
# 	corner_points.append(cfg["image_parameters"]["p1"])
# 	corner_points.append(cfg["image_parameters"]["p2"])
# 	corner_points.append(cfg["image_parameters"]["p3"])
# 	corner_points.append(cfg["image_parameters"]["p4"])
# 	width_og = int(cfg["image_parameters"]["width_og"])
# 	height_og = int(cfg["image_parameters"]["height_og"])
# 	img_path = cfg["image_parameters"]["img_path"]
# 	size_frame = cfg["image_parameters"]["size_frame"]
# print(bcolors.OKGREEN +" Done : [ Config file loaded ] ..."+bcolors.ENDC )


######################################### 
#		     Select the model 			#
#########################################
# model_names_list = [name for name in os.listdir("../models/.") if name.find(".") == -1]
# for index,model_name in enumerate(model_names_list):
#     print(" - {} [{}]".format(model_name,index))
# model_num = input(" Please select the number related to the model that you want : ")
# if model_num == "":
# 	model_path="../models/faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb" 
# else :
# 	model_path = "../models/"+model_names_list[int(model_num)]+"/frozen_inference_graph.pb"
# print(bcolors.WARNING + " [ Loading the TENSORFLOW MODEL ... ]"+bcolors.ENDC)
#model = Model('app/monitor/models/ssdlite_mobiledet_cpu_320x320_coco_2020_05_19/model.tflite')
# print(bcolors.OKGREEN +"Done : [ Model loaded and initialized ] ..."+bcolors.ENDC)


######################################### 
#		     Select the video 			#
#########################################
# video_names_list = [name for name in os.listdir("../video/") if name.endswith(".mp4") or name.endswith(".avi")]
# for index,video_name in enumerate(video_names_list):
#     print(" - {} [{}]".format(video_name,index))
# video_num = input("Enter the exact name of the video (including .mp4 or else) : ")
# if video_num == "":
# 	video_path="../video/PETS2009.avi"  
# else :
# 	video_path = "../video/"+video_names_list[int(video_num)]


######################################### 
#		    Minimal distance			#
#########################################
#distance_minimum = input("Prompt the size of the minimal distance between 2 pedestrians : ")
# if distance_minimum == "":
# 	distance_minimum = "110"


######################################### 
#     Compute transformation matrix		#
#########################################
# Compute  transformation matrix from the original frame
# matrix,imgOutput = compute_perspective_transform(corner_points,width_og,height_og,cv2.imread(img_path))
# height,width,_ = imgOutput.shape
# blank_image = np.zeros((height,width,3), np.uint8)
# height = blank_image.shape[0]
# width = blank_image.shape[1] 
# dim = (width, height)




######################################################
#########									 #########
# 				START THE VIDEO STREAM               #
#########									 #########
######################################################

# def gen_frames():
# 	vs = cv2.VideoCapture(0)
# 	output_video_1,output_video_2 = None,None
# 	# Loop until the end of the video stream
# 	while True:	
# 		# Load the image of the ground and resize it to the correct size
# 		img = cv2.imread("app/monitor/img/chemin_1.png")
# 		bird_view_img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
		
# 		# Load the frame
# 		(frame_exists, frame) = vs.read()
# 		# Test if it has reached the end of the video
# 		if not frame_exists:
# 			break
# 		else:
# 			# Resize the image to the correct size
# 			#frame = imutils.resize(frame, width=int(size_frame))
			
# 			# Make the predictions for this frame
# 			(boxes, scores, classes) =  model.predict(frame)

# 			# Get the human detected in the frame and return the 2 points to build the bounding box  
# 			array_boxes_detected = get_human_box_detection(boxes,scores,classes,frame.shape[0],frame.shape[1])
			
# 			# Both of our lists that will contain the centroïds coordonates and the ground points
# 			array_centroids,array_groundpoints = get_centroids_and_groundpoints(array_boxes_detected)

# 			# Use the transform matrix to get the transformed coordonates
# 			transformed_downoids = compute_point_perspective_transformation(matrix,array_groundpoints)
			
# 			# Show every point on the top view image 
# 			for point in transformed_downoids:
# 				x,y = point
# 				cv2.circle(bird_view_img, (int(x),int(y)), BIG_CIRCLE, COLOR_GREEN, 2)
# 				cv2.circle(bird_view_img, (int(x),int(y)), SMALL_CIRCLE, COLOR_GREEN, -1)

# 			# Check if 2 or more people have been detected (otherwise no need to detect)
# 			if len(transformed_downoids) >= 2:
# 				for index,downoid in enumerate(transformed_downoids):
# 					if not (downoid[0] > width or downoid[0] < 0 or downoid[1] > height+200 or downoid[1] < 0 ):
# 						cv2.rectangle(frame,(array_boxes_detected[index][1],array_boxes_detected[index][0]),(array_boxes_detected[index][3],array_boxes_detected[index][2]),COLOR_GREEN,2)

# 				# Iterate over every possible 2 by 2 between the points combinations 
# 				list_indexes = list(itertools.combinations(range(len(transformed_downoids)), 2))
# 				for i,pair in enumerate(itertools.combinations(transformed_downoids, r=2)):
# 					# Check if the distance between each combination of points is less than the minimum distance chosen
# 					if math.sqrt( (pair[0][0] - pair[1][0])**2 + (pair[0][1] - pair[1][1])**2 ) < int(distance_minimum):
# 						# Change the colors of the points that are too close from each other to red
# 						if not (pair[0][0] > width or pair[0][0] < 0 or pair[0][1] > height+200  or pair[0][1] < 0 or pair[1][0] > width or pair[1][0] < 0 or pair[1][1] > height+200  or pair[1][1] < 0):
# 							change_color_on_topview(pair)
# 							# Get the equivalent indexes of these points in the original frame and change the color to red
# 							index_pt1 = list_indexes[i][0]
# 							index_pt2 = list_indexes[i][1]
# 							cv2.rectangle(frame,(array_boxes_detected[index_pt1][1],array_boxes_detected[index_pt1][0]),(array_boxes_detected[index_pt1][3],array_boxes_detected[index_pt1][2]),COLOR_RED,2)
# 							cv2.rectangle(frame,(array_boxes_detected[index_pt2][1],array_boxes_detected[index_pt2][0]),(array_boxes_detected[index_pt2][3],array_boxes_detected[index_pt2][2]),COLOR_RED,2)

# 			ret, buffer = cv2.imencode('.jpg', frame)
# 			bframe = buffer.tobytes()
# 			yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + bframe + b'\r\n')  # concat frame one by one and show result
		# Draw the green rectangle to delimitate the detection zone
		#draw_rectangle(corner_points) 
		# # Show both images	
		# cv2.imshow("Bird view", bird_view_img)
		# cv2.imshow("Original picture", frame)


		# key = cv2.waitKey(1) & 0xFF

		# # Write the both outputs video to a local folders
		# if output_video_1 is None and output_video_2 is None:
		# 	fourcc1 = cv2.VideoWriter_fourcc(*"MJPG")
		# 	output_video_1 = cv2.VideoWriter("../output/video.avi", fourcc1, 25,(frame.shape[1], frame.shape[0]), True)
		# 	fourcc2 = cv2.VideoWriter_fourcc(*"MJPG")
		# 	output_video_2 = cv2.VideoWriter("../output/bird_view.avi", fourcc2, 25,(bird_view_img.shape[1], bird_view_img.shape[0]), True)
		# elif output_video_1 is not None and output_video_2 is not None:
		# 	output_video_1.write(frame)
		# 	output_video_2.write(bird_view_img)

		# # Break the loop
		# if key == ord("q"):
		# 	break
