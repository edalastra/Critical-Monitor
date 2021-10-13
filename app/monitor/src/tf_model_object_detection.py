import numpy as np
import tensorflow as tf
from tensorflow.lite.python.interpreter import Interpreter
import cv2
import time


# MODEL_NAME = args.modeldir
# GRAPH_NAME = args.graph
# LABELMAP_NAME = args.labels
# VIDEO_NAME = args.video
# min_conf_threshold = float(args.threshold)
# use_TPU = False

class Model:
    """
    Class that contains the model and all its functions
    """
    def __init__(self, model_path):
        """
        Initialization function
        @ model_path : path to the model 
        """
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2] 
        self.floating_model = (self.input_details[0]['dtype'] == np.float32)

        self.input_mean = 127.5
        self.input_std = 127.5


        # Declare detection graph
        self.detection_graph = tf.Graph()
        # Load the model into the tensorflow graph
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(model_path, 'rb') as file:
                serialized_graph = file.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        # Create a session from the detection graph
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)

    def predict(self,img):
        frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if self.floating_model:
            input_data = (np.float32(input_data) - self.input_mean) / self.input_std

        # Perform the actual detection by running the model with the image as input
        self.interpreter.set_tensor(self.input_details[0]['index'],input_data)
        self.interpreter.invoke()

        # Retrieve detection results
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]  # Class index of detected objects
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0] # Confidence of detected objects

        """
        Get the predicition results on 1 frame
        @ img : our img vector
        """
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        #img_exp = np.expand_dims(img, axis=0)
        # Pass the inputs and outputs to the session to get the results 
        #(boxes, scores, classes) = self.sess.run([self.detection_graph.get_tensor_by_name('detection_boxes:0'), self.detection_graph.get_tensor_by_name('detection_scores:0'), self.detection_graph.get_tensor_by_name('detection_classes:0')],feed_dict={self.detection_graph.get_tensor_by_name('image_tensor:0'): img_exp})
        return (boxes, scores, classes)  

