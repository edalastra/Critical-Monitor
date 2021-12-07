import numpy as np
from scipy.linalg.basic import det
import tensorflow as tf
from tensorflow.lite.python.interpreter import Interpreter
import cv2
import time
from app.monitor.core.yolov4 import filter_boxes
from app.monitor.deep_sort import nn_matching, preprocessing
from app.monitor.deep_sort.detection import Detection
from app.monitor.tools import generate_detections as gdet
from app.monitor.deep_sort.tracker import Tracker
from app.monitor.core.utils import format_boxes
from absl import app, flags, logging  # argparse 대용인가?; (ref) https://github.com/abseil/abseil-py
from absl.flags import FLAGS
from tensorflow.compat.v1 import InteractiveSession, ConfigProto

flags.DEFINE_string('framework', 'tflite', 'TF lite' )
flags.DEFINE_string('weights', './checkpoints/yolov4-tiny-416.tflite', 'path to weights file')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_boolean('tiny', True, 'yolo-tiny moodel')
flags.DEFINE_string('model', 'yolov4', 'yolov3 or yolov4')
flags.DEFINE_string('output', 'result.png', 'path to output image')
flags.DEFINE_float('iou', 0.45, 'iou threshold')
flags.DEFINE_float('score', 0.45, 'score threshold')
flags.DEFINE_boolean('dont_show', False, 'dont show video output')
flags.DEFINE_boolean('info', False, 'show detailed info of tracked objects')
flags.DEFINE_boolean('count', False, 'count objects being tracked on screen')

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
        config = ConfigProto()
        config.gpu_options.allow_growth = True    
        self.session = InteractiveSession(config=config)

        self.interpreter =  tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2] 
        self.floating_model = (self.input_details[0]['dtype'] == np.float32)

        self.input_mean = 127.0
        self.input_std = 127.5
        max_cosine_distance = 0.4
        nn_budget = None
        self.nms_max_overlap = 1.0
        self.encoder = gdet.create_box_encoder('app/monitor/models/mars-small128.pb', batch_size=1)
        metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)

        # initialize tracker
        self.tracker = Tracker(metric)


        # # Declare detection graph
        # self.detection_graph = tf.Graph()
        # # Load the model into the tensorflow graph
        # with self.detection_graph.as_default():
        #     od_graph_def = tf.compat.v1.GraphDef()
        #     with tf.io.gfile.GFile(model_path, 'rb') as file:
        #         serialized_graph = file.read()
        #         od_graph_def.ParseFromString(serialized_graph)
        #         tf.import_graph_def(od_graph_def, name='')

        # # Create a session from the detection graph
        # self.sess = tf.compat.v1.Session(graph=self.detection_graph)

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
        return  (boxes, scores, classes)

    def model_inference(self, image_input ):
        frame = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)

        image_data = cv2.resize(frame, (416, 416))
        image_data = image_data / 255.
        image_data = image_data[np.newaxis, ...].astype(np.float32)
       
        self.interpreter.set_tensor(self.input_details[0]['index'], image_data)
        self.interpreter.invoke()
        pred = [self.interpreter.get_tensor(self.output_details[i]['index']) for i in range(len(self.output_details))]

        boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25, input_shape=tf.constant([416, 416]))

        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=0.45,
            score_threshold=0.45
            )
            
        num_objects = valid_detections.numpy()[0]
        bboxes = boxes.numpy()[0]
        bboxes = bboxes[0:int(num_objects)]
        scores_npy = scores.numpy()[0]
        scores_npy = scores_npy[0:int(num_objects)]
        classes_npy = classes.numpy()[0]
        classes_npy = classes_npy[0:int(num_objects)]

        original_h, original_w, _ = frame.shape
        bboxes = format_boxes(bboxes, original_h, original_w)

        pred_bbox = [bboxes, scores_npy, classes_npy , num_objects]

        names = np.array(['person' for _ in range(num_objects)])
        count = len(names)
    
        """ Tracking 
        # """
        # if FLAGS.count:
        #     cv2.putText(frame, "Objects being tracked: {}".format(count), (5, 35), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 2)
        print("Objects being tracked: {}".format(count))

        # encode yolo detections and feed to tracker
        features = self.encoder(frame, bboxes)
        detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in zip(bboxes, scores_npy, names, features)]


        # run non-maxima supression
        boxs = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        classes = np.array([d.class_name for d in detections])
        indices = preprocessing.non_max_suppression(boxs, classes, self.nms_max_overlap, scores)
        detections = [detections[i] for i in indices]       

        # Call the tracker
        self.tracker.predict()
        self.tracker.update(detections)

        # update tracks
        indexIDs = []
        bauxis = []
        for track in self.tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue         
            indexIDs.append(int(track.track_id))
            bbox = track.to_tlbr()
            bauxis.append([int(bbox[1]), int(bbox[0]), int(bbox[3]), int(bbox[2])])

        # update tracks
        return  bauxis, scores_npy, classes_npy, indexIDs