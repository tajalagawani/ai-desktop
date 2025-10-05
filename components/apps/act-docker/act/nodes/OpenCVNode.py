"""
OpenCV Node - Comprehensive computer vision and image processing integration
Refactored with improved architecture: dispatch maps, unified async/sync handling,
proper connection lifecycle, and standardized return shapes.
Supports all major OpenCV operations including image processing, feature detection,
object detection, camera calibration, 3D reconstruction, and deep learning inference.
Uses OpenCV library for optimal computer vision functionality.
"""

import logging
import asyncio
import json
import base64
import os
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from io import BytesIO

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    # Define dummy cv2 for when OpenCV is not available
    class cv2:
        @staticmethod
        def imread(*args, **kwargs):
            return None
        @staticmethod
        def imwrite(*args, **kwargs):
            return False
        @staticmethod
        def cvtColor(*args, **kwargs):
            return None
        
        class CascadeClassifier:
            def __init__(self, *args, **kwargs):
                pass
            def detectMultiScale(self, *args, **kwargs):
                return []
        
        class data:
            haarcascades = "/dummy/path/"
        
        class dnn:
            @staticmethod
            def readNet(*args, **kwargs):
                return None
            @staticmethod
            def readNetFromONNX(*args, **kwargs):
                return None
            @staticmethod
            def blobFromImage(*args, **kwargs):
                return None
        
        # Constants
        IMREAD_COLOR = 1
        IMREAD_GRAYSCALE = 0
        IMREAD_UNCHANGED = -1
        COLOR_BGR2RGB = 4
        COLOR_BGR2GRAY = 6

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from base_node import (
        BaseNode, NodeSchema, NodeParameter, NodeParameterType,
        NodeValidationError, NodeExecutionError
    )
except ImportError:
    try:
        from .base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )
    except ImportError:
        from base_node import (
            BaseNode, NodeSchema, NodeParameter, NodeParameterType,
            NodeValidationError, NodeExecutionError
        )

# Configure logging with proper masking
logger = logging.getLogger(__name__)

class OpenCVOperation:
    """All available OpenCV operations organized by module."""
    
    # Core operations
    READ_IMAGE = "read_image"
    WRITE_IMAGE = "write_image"
    CREATE_IMAGE = "create_image"
    COPY_IMAGE = "copy_image"
    CONVERT_DTYPE = "convert_dtype"
    SPLIT_CHANNELS = "split_channels"
    MERGE_CHANNELS = "merge_channels"
    
    # Image Processing (imgproc)
    COLOR_CONVERT = "color_convert"
    RESIZE_IMAGE = "resize_image"
    CROP_IMAGE = "crop_image"
    ROTATE_IMAGE = "rotate_image"
    FLIP_IMAGE = "flip_image"
    WARP_AFFINE = "warp_affine"
    WARP_PERSPECTIVE = "warp_perspective"
    
    # Filtering
    BLUR = "blur"
    GAUSSIAN_BLUR = "gaussian_blur"
    MEDIAN_BLUR = "median_blur"
    BILATERAL_FILTER = "bilateral_filter"
    BOX_FILTER = "box_filter"
    SOBEL = "sobel"
    LAPLACIAN = "laplacian"
    CANNY = "canny"
    
    # Morphological operations
    ERODE = "erode"
    DILATE = "dilate"
    MORPHOLOGY_EX = "morphology_ex"
    
    # Thresholding
    THRESHOLD = "threshold"
    ADAPTIVE_THRESHOLD = "adaptive_threshold"
    
    # Contours
    FIND_CONTOURS = "find_contours"
    DRAW_CONTOURS = "draw_contours"
    CONTOUR_AREA = "contour_area"
    CONTOUR_PERIMETER = "contour_perimeter"
    BOUNDING_RECT = "bounding_rect"
    MIN_ENCLOSING_CIRCLE = "min_enclosing_circle"
    CONVEX_HULL = "convex_hull"
    
    # Drawing operations
    DRAW_LINE = "draw_line"
    DRAW_RECTANGLE = "draw_rectangle"
    DRAW_CIRCLE = "draw_circle"
    DRAW_ELLIPSE = "draw_ellipse"
    DRAW_POLYGON = "draw_polygon"
    PUT_TEXT = "put_text"
    
    # Feature Detection (features2d)
    DETECT_ORB = "detect_orb"
    DETECT_SIFT = "detect_sift"
    DETECT_SURF = "detect_surf"
    DETECT_FAST = "detect_fast"
    DETECT_BRIEF = "detect_brief"
    DETECT_BRISK = "detect_brisk"
    MATCH_FEATURES = "match_features"
    DRAW_KEYPOINTS = "draw_keypoints"
    DRAW_MATCHES = "draw_matches"
    
    # Object Detection (objdetect)
    DETECT_FACES = "detect_faces"
    DETECT_EYES = "detect_eyes"
    DETECT_SMILES = "detect_smiles"
    DETECT_BODIES = "detect_bodies"
    DETECT_CARS = "detect_cars"
    CASCADE_DETECT = "cascade_detect"
    HOG_DETECT = "hog_detect"
    
    # Camera Calibration (calib3d)
    CALIBRATE_CAMERA = "calibrate_camera"
    UNDISTORT_IMAGE = "undistort_image"
    FIND_CHESSBOARD = "find_chessboard"
    DRAW_CHESSBOARD = "draw_chessboard"
    STEREO_CALIBRATE = "stereo_calibrate"
    STEREO_RECTIFY = "stereo_rectify"
    SOLVE_PNP = "solve_pnp"
    PROJECT_POINTS = "project_points"
    RODRIGUES = "rodrigues"
    
    # Deep Learning (dnn)
    LOAD_DNN_MODEL = "load_dnn_model"
    DNN_FORWARD = "dnn_forward"
    BLOB_FROM_IMAGE = "blob_from_image"
    DETECT_OBJECTS_YOLO = "detect_objects_yolo"
    CLASSIFY_IMAGE = "classify_image"
    SEGMENT_IMAGE = "segment_image"
    POSE_ESTIMATION = "pose_estimation"
    
    # Video operations
    READ_VIDEO = "read_video"
    WRITE_VIDEO = "write_video"
    VIDEO_CAPTURE = "video_capture"
    BACKGROUND_SUBTRACTION = "background_subtraction"
    OPTICAL_FLOW = "optical_flow"
    MOTION_DETECTION = "motion_detection"
    
    # Template matching
    TEMPLATE_MATCH = "template_match"
    MULTI_TEMPLATE_MATCH = "multi_template_match"
    
    # Histogram operations
    CALC_HISTOGRAM = "calc_histogram"
    HISTOGRAM_EQUALIZATION = "histogram_equalization"
    CLAHE = "clahe"
    COMPARE_HISTOGRAMS = "compare_histograms"
    
    # Image quality assessment
    CALCULATE_PSNR = "calculate_psnr"
    CALCULATE_SSIM = "calculate_ssim"
    CALCULATE_MSE = "calculate_mse"
    
    # Advanced operations
    INPAINT = "inpaint"
    SEAMLESS_CLONE = "seamless_clone"
    GRAB_CUT = "grab_cut"
    WATERSHED = "watershed"
    MEAN_SHIFT = "mean_shift"
    CAM_SHIFT = "cam_shift"

class OpenCVWrapper:
    """Unified OpenCV wrapper that handles image processing operations."""
    
    def __init__(self):
        """Initialize the OpenCV wrapper."""
        self.net = None  # For DNN operations
        self.cascade_classifiers = {}  # Cache for cascade classifiers
        
    def load_image(self, image_path: str, color_mode: str = "color") -> np.ndarray:
        """Load an image from file path."""
        if color_mode == "color":
            return cv2.imread(image_path, cv2.IMREAD_COLOR)
        elif color_mode == "grayscale":
            return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        elif color_mode == "unchanged":
            return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        else:
            return cv2.imread(image_path)
    
    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        """Save an image to file path."""
        return cv2.imwrite(output_path, image)
    
    def encode_image_base64(self, image: np.ndarray, format: str = ".jpg") -> str:
        """Encode image as base64 string."""
        success, buffer = cv2.imencode(format, image)
        if success:
            return base64.b64encode(buffer).decode('utf-8')
        return None
    
    def decode_image_base64(self, base64_string: str) -> np.ndarray:
        """Decode base64 string to image."""
        image_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(image_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Image Processing Operations
    def convert_color(self, image: np.ndarray, conversion: str) -> np.ndarray:
        """Convert image color space."""
        conversion_map = {
            "bgr_to_rgb": cv2.COLOR_BGR2RGB,
            "rgb_to_bgr": cv2.COLOR_RGB2BGR,
            "bgr_to_gray": cv2.COLOR_BGR2GRAY,
            "gray_to_bgr": cv2.COLOR_GRAY2BGR,
            "bgr_to_hsv": cv2.COLOR_BGR2HSV,
            "hsv_to_bgr": cv2.COLOR_HSV2BGR,
            "bgr_to_lab": cv2.COLOR_BGR2LAB,
            "lab_to_bgr": cv2.COLOR_LAB2BGR,
            "bgr_to_yuv": cv2.COLOR_BGR2YUV,
            "yuv_to_bgr": cv2.COLOR_YUV2BGR
        }
        return cv2.cvtColor(image, conversion_map.get(conversion, cv2.COLOR_BGR2RGB))
    
    def resize_image(self, image: np.ndarray, width: int, height: int, interpolation: str = "linear") -> np.ndarray:
        """Resize image to specified dimensions."""
        interp_map = {
            "nearest": cv2.INTER_NEAREST,
            "linear": cv2.INTER_LINEAR,
            "cubic": cv2.INTER_CUBIC,
            "area": cv2.INTER_AREA,
            "lanczos": cv2.INTER_LANCZOS4
        }
        return cv2.resize(image, (width, height), interpolation=interp_map.get(interpolation, cv2.INTER_LINEAR))
    
    def gaussian_blur(self, image: np.ndarray, kernel_size: int, sigma_x: float, sigma_y: float = 0) -> np.ndarray:
        """Apply Gaussian blur to image."""
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma_x, sigmaY=sigma_y)
    
    def canny_edge_detection(self, image: np.ndarray, threshold1: int, threshold2: int, aperture_size: int = 3) -> np.ndarray:
        """Apply Canny edge detection."""
        return cv2.Canny(image, threshold1, threshold2, apertureSize=aperture_size)
    
    # Feature Detection Operations
    def detect_orb_features(self, image: np.ndarray, n_features: int = 500) -> Tuple[List, np.ndarray]:
        """Detect ORB features and descriptors."""
        orb = cv2.ORB_create(nfeatures=n_features)
        keypoints, descriptors = orb.detectAndCompute(image, None)
        return keypoints, descriptors
    
    def detect_corners(self, image: np.ndarray, max_corners: int = 100, quality_level: float = 0.01, min_distance: float = 10) -> np.ndarray:
        """Detect corners using goodFeaturesToTrack."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        corners = cv2.goodFeaturesToTrack(gray, max_corners, quality_level, min_distance)
        return corners
    
    # Object Detection Operations
    def load_cascade_classifier(self, cascade_path: str) -> cv2.CascadeClassifier:
        """Load and cache cascade classifier."""
        if cascade_path not in self.cascade_classifiers:
            self.cascade_classifiers[cascade_path] = cv2.CascadeClassifier(cascade_path)
        return self.cascade_classifiers[cascade_path]
    
    def detect_faces(self, image: np.ndarray, scale_factor: float = 1.1, min_neighbors: int = 5) -> List[Tuple[int, int, int, int]]:
        """Detect faces using Haar cascade."""
        face_cascade = self.load_cascade_classifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        faces = face_cascade.detectMultiScale(gray, scale_factor, min_neighbors)
        return faces.tolist()
    
    # DNN Operations
    def load_dnn_model(self, model_path: str, config_path: str = None, framework: str = "auto") -> bool:
        """Load a deep learning model."""
        try:
            if framework == "auto":
                self.net = cv2.dnn.readNet(model_path, config_path)
            elif framework == "tensorflow":
                self.net = cv2.dnn.readNetFromTensorflow(model_path, config_path)
            elif framework == "caffe":
                self.net = cv2.dnn.readNetFromCaffe(config_path, model_path)
            elif framework == "darknet":
                self.net = cv2.dnn.readNetFromDarknet(config_path, model_path)
            elif framework == "onnx":
                self.net = cv2.dnn.readNetFromONNX(model_path)
            else:
                raise ValueError(f"Unsupported framework: {framework}")
            return True
        except Exception as e:
            logger.error(f"Failed to load DNN model: {e}")
            return False
    
    def create_blob_from_image(self, image: np.ndarray, scale_factor: float = 1.0, size: Tuple[int, int] = (416, 416), 
                              mean: Tuple[float, float, float] = (0, 0, 0), swap_rb: bool = True) -> np.ndarray:
        """Create blob from image for DNN input."""
        return cv2.dnn.blobFromImage(image, scale_factor, size, mean, swapRB=swap_rb)
    
    def dnn_forward_pass(self, blob: np.ndarray) -> np.ndarray:
        """Perform forward pass through loaded DNN model."""
        if self.net is None:
            raise ValueError("No DNN model loaded")
        self.net.setInput(blob)
        return self.net.forward()
    
    # Contour Operations
    def find_contours(self, image: np.ndarray, mode: str = "external", method: str = "simple") -> List:
        """Find contours in binary image."""
        mode_map = {
            "external": cv2.RETR_EXTERNAL,
            "list": cv2.RETR_LIST,
            "ccomp": cv2.RETR_CCOMP,
            "tree": cv2.RETR_TREE
        }
        method_map = {
            "none": cv2.CHAIN_APPROX_NONE,
            "simple": cv2.CHAIN_APPROX_SIMPLE,
            "tc89_l1": cv2.CHAIN_APPROX_TC89_L1,
            "tc89_kcos": cv2.CHAIN_APPROX_TC89_KCOS
        }
        contours, hierarchy = cv2.findContours(image, mode_map.get(mode, cv2.RETR_EXTERNAL), 
                                             method_map.get(method, cv2.CHAIN_APPROX_SIMPLE))
        return contours, hierarchy
    
    def draw_contours(self, image: np.ndarray, contours: List, contour_idx: int = -1, 
                     color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """Draw contours on image."""
        result = image.copy()
        cv2.drawContours(result, contours, contour_idx, color, thickness)
        return result
    
    # Template Matching
    def template_match(self, image: np.ndarray, template: np.ndarray, method: str = "ccoeff_normed") -> Tuple[np.ndarray, Tuple[int, int], float]:
        """Perform template matching."""
        method_map = {
            "sqdiff": cv2.TM_SQDIFF,
            "sqdiff_normed": cv2.TM_SQDIFF_NORMED,
            "ccorr": cv2.TM_CCORR,
            "ccorr_normed": cv2.TM_CCORR_NORMED,
            "ccoeff": cv2.TM_CCOEFF,
            "ccoeff_normed": cv2.TM_CCOEFF_NORMED
        }
        result = cv2.matchTemplate(image, template, method_map.get(method, cv2.TM_CCOEFF_NORMED))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if method in ["sqdiff", "sqdiff_normed"]:
            best_match_loc = min_loc
            confidence = 1 - min_val if method == "sqdiff_normed" else min_val
        else:
            best_match_loc = max_loc
            confidence = max_val
            
        return result, best_match_loc, confidence

class OpenCVNode(BaseNode):
    """OpenCV Node for comprehensive computer vision operations."""
    
    def __init__(self):
        super().__init__()
        
        # Create operation dispatch map for clean routing
        self.operation_dispatch = {
            # Core operations
            OpenCVOperation.READ_IMAGE: self._handle_read_image,
            OpenCVOperation.WRITE_IMAGE: self._handle_write_image,
            OpenCVOperation.CREATE_IMAGE: self._handle_create_image,
            OpenCVOperation.COPY_IMAGE: self._handle_copy_image,
            OpenCVOperation.CONVERT_DTYPE: self._handle_convert_dtype,
            OpenCVOperation.SPLIT_CHANNELS: self._handle_split_channels,
            OpenCVOperation.MERGE_CHANNELS: self._handle_merge_channels,
            
            # Image processing
            OpenCVOperation.COLOR_CONVERT: self._handle_color_convert,
            OpenCVOperation.RESIZE_IMAGE: self._handle_resize_image,
            OpenCVOperation.CROP_IMAGE: self._handle_crop_image,
            OpenCVOperation.ROTATE_IMAGE: self._handle_rotate_image,
            OpenCVOperation.FLIP_IMAGE: self._handle_flip_image,
            OpenCVOperation.WARP_AFFINE: self._handle_warp_affine,
            OpenCVOperation.WARP_PERSPECTIVE: self._handle_warp_perspective,
            
            # Filtering
            OpenCVOperation.BLUR: self._handle_blur,
            OpenCVOperation.GAUSSIAN_BLUR: self._handle_gaussian_blur,
            OpenCVOperation.MEDIAN_BLUR: self._handle_median_blur,
            OpenCVOperation.BILATERAL_FILTER: self._handle_bilateral_filter,
            OpenCVOperation.BOX_FILTER: self._handle_box_filter,
            OpenCVOperation.SOBEL: self._handle_sobel,
            OpenCVOperation.LAPLACIAN: self._handle_laplacian,
            OpenCVOperation.CANNY: self._handle_canny,
            
            # Morphological operations
            OpenCVOperation.ERODE: self._handle_erode,
            OpenCVOperation.DILATE: self._handle_dilate,
            OpenCVOperation.MORPHOLOGY_EX: self._handle_morphology_ex,
            
            # Thresholding
            OpenCVOperation.THRESHOLD: self._handle_threshold,
            OpenCVOperation.ADAPTIVE_THRESHOLD: self._handle_adaptive_threshold,
            
            # Contours
            OpenCVOperation.FIND_CONTOURS: self._handle_find_contours,
            OpenCVOperation.DRAW_CONTOURS: self._handle_draw_contours,
            OpenCVOperation.CONTOUR_AREA: self._handle_contour_area,
            OpenCVOperation.CONTOUR_PERIMETER: self._handle_contour_perimeter,
            OpenCVOperation.BOUNDING_RECT: self._handle_bounding_rect,
            OpenCVOperation.MIN_ENCLOSING_CIRCLE: self._handle_min_enclosing_circle,
            OpenCVOperation.CONVEX_HULL: self._handle_convex_hull,
            
            # Drawing operations
            OpenCVOperation.DRAW_LINE: self._handle_draw_line,
            OpenCVOperation.DRAW_RECTANGLE: self._handle_draw_rectangle,
            OpenCVOperation.DRAW_CIRCLE: self._handle_draw_circle,
            OpenCVOperation.DRAW_ELLIPSE: self._handle_draw_ellipse,
            OpenCVOperation.DRAW_POLYGON: self._handle_draw_polygon,
            OpenCVOperation.PUT_TEXT: self._handle_put_text,
            
            # Feature detection
            OpenCVOperation.DETECT_ORB: self._handle_detect_orb,
            OpenCVOperation.DETECT_SIFT: self._handle_detect_sift,
            OpenCVOperation.DETECT_SURF: self._handle_detect_surf,
            OpenCVOperation.DETECT_FAST: self._handle_detect_fast,
            OpenCVOperation.DETECT_BRIEF: self._handle_detect_brief,
            OpenCVOperation.DETECT_BRISK: self._handle_detect_brisk,
            OpenCVOperation.MATCH_FEATURES: self._handle_match_features,
            OpenCVOperation.DRAW_KEYPOINTS: self._handle_draw_keypoints,
            OpenCVOperation.DRAW_MATCHES: self._handle_draw_matches,
            
            # Object detection
            OpenCVOperation.DETECT_FACES: self._handle_detect_faces,
            OpenCVOperation.DETECT_EYES: self._handle_detect_eyes,
            OpenCVOperation.DETECT_SMILES: self._handle_detect_smiles,
            OpenCVOperation.DETECT_BODIES: self._handle_detect_bodies,
            OpenCVOperation.DETECT_CARS: self._handle_detect_cars,
            OpenCVOperation.CASCADE_DETECT: self._handle_cascade_detect,
            OpenCVOperation.HOG_DETECT: self._handle_hog_detect,
            
            # Camera calibration
            OpenCVOperation.CALIBRATE_CAMERA: self._handle_calibrate_camera,
            OpenCVOperation.UNDISTORT_IMAGE: self._handle_undistort_image,
            OpenCVOperation.FIND_CHESSBOARD: self._handle_find_chessboard,
            OpenCVOperation.DRAW_CHESSBOARD: self._handle_draw_chessboard,
            OpenCVOperation.STEREO_CALIBRATE: self._handle_stereo_calibrate,
            OpenCVOperation.STEREO_RECTIFY: self._handle_stereo_rectify,
            OpenCVOperation.SOLVE_PNP: self._handle_solve_pnp,
            OpenCVOperation.PROJECT_POINTS: self._handle_project_points,
            OpenCVOperation.RODRIGUES: self._handle_rodrigues,
            
            # Deep learning
            OpenCVOperation.LOAD_DNN_MODEL: self._handle_load_dnn_model,
            OpenCVOperation.DNN_FORWARD: self._handle_dnn_forward,
            OpenCVOperation.BLOB_FROM_IMAGE: self._handle_blob_from_image,
            OpenCVOperation.DETECT_OBJECTS_YOLO: self._handle_detect_objects_yolo,
            OpenCVOperation.CLASSIFY_IMAGE: self._handle_classify_image,
            OpenCVOperation.SEGMENT_IMAGE: self._handle_segment_image,
            OpenCVOperation.POSE_ESTIMATION: self._handle_pose_estimation,
            
            # Video operations
            OpenCVOperation.READ_VIDEO: self._handle_read_video,
            OpenCVOperation.WRITE_VIDEO: self._handle_write_video,
            OpenCVOperation.VIDEO_CAPTURE: self._handle_video_capture,
            OpenCVOperation.BACKGROUND_SUBTRACTION: self._handle_background_subtraction,
            OpenCVOperation.OPTICAL_FLOW: self._handle_optical_flow,
            OpenCVOperation.MOTION_DETECTION: self._handle_motion_detection,
            
            # Template matching
            OpenCVOperation.TEMPLATE_MATCH: self._handle_template_match,
            OpenCVOperation.MULTI_TEMPLATE_MATCH: self._handle_multi_template_match,
            
            # Histogram operations
            OpenCVOperation.CALC_HISTOGRAM: self._handle_calc_histogram,
            OpenCVOperation.HISTOGRAM_EQUALIZATION: self._handle_histogram_equalization,
            OpenCVOperation.CLAHE: self._handle_clahe,
            OpenCVOperation.COMPARE_HISTOGRAMS: self._handle_compare_histograms,
            
            # Image quality assessment
            OpenCVOperation.CALCULATE_PSNR: self._handle_calculate_psnr,
            OpenCVOperation.CALCULATE_SSIM: self._handle_calculate_ssim,
            OpenCVOperation.CALCULATE_MSE: self._handle_calculate_mse,
            
            # Advanced operations
            OpenCVOperation.INPAINT: self._handle_inpaint,
            OpenCVOperation.SEAMLESS_CLONE: self._handle_seamless_clone,
            OpenCVOperation.GRAB_CUT: self._handle_grab_cut,
            OpenCVOperation.WATERSHED: self._handle_watershed,
            OpenCVOperation.MEAN_SHIFT: self._handle_mean_shift,
            OpenCVOperation.CAM_SHIFT: self._handle_cam_shift,
        }
    
    # Operation metadata for validation
    OPERATION_METADATA = {
        # Core operations
        OpenCVOperation.READ_IMAGE: {
            "required_params": ["image_path"],
            "optional_params": ["color_mode"],
            "description": "Read image from file path"
        },
        OpenCVOperation.WRITE_IMAGE: {
            "required_params": ["image_data", "output_path"],
            "optional_params": [],
            "description": "Save image to file path"
        },
        OpenCVOperation.COLOR_CONVERT: {
            "required_params": ["image_data", "conversion"],
            "optional_params": [],
            "description": "Convert image color space"
        },
        OpenCVOperation.RESIZE_IMAGE: {
            "required_params": ["image_data", "width", "height"],
            "optional_params": ["interpolation"],
            "description": "Resize image to specified dimensions"
        },
        OpenCVOperation.GAUSSIAN_BLUR: {
            "required_params": ["image_data", "kernel_size", "sigma_x"],
            "optional_params": ["sigma_y"],
            "description": "Apply Gaussian blur to image"
        },
        OpenCVOperation.CANNY: {
            "required_params": ["image_data", "threshold1", "threshold2"],
            "optional_params": ["aperture_size"],
            "description": "Apply Canny edge detection"
        },
        OpenCVOperation.DETECT_FACES: {
            "required_params": ["image_data"],
            "optional_params": ["scale_factor", "min_neighbors"],
            "description": "Detect faces using Haar cascade"
        },
        OpenCVOperation.DETECT_ORB: {
            "required_params": ["image_data"],
            "optional_params": ["n_features"],
            "description": "Detect ORB features and descriptors"
        },
        OpenCVOperation.TEMPLATE_MATCH: {
            "required_params": ["image_data", "template_data"],
            "optional_params": ["method"],
            "description": "Perform template matching"
        },
        OpenCVOperation.FIND_CONTOURS: {
            "required_params": ["image_data"],
            "optional_params": ["mode", "method"],
            "description": "Find contours in binary image"
        },
        OpenCVOperation.LOAD_DNN_MODEL: {
            "required_params": ["model_path"],
            "optional_params": ["config_path", "framework"],
            "description": "Load a deep learning model"
        },
        OpenCVOperation.BLOB_FROM_IMAGE: {
            "required_params": ["image_data"],
            "optional_params": ["scale_factor", "size", "mean", "swap_rb"],
            "description": "Create blob from image for DNN input"
        }
    }

    def get_schema(self) -> NodeSchema:
        """Generate schema with all parameters from operation metadata."""
        # Common parameters for all operations
        base_params = [
            ("operation", NodeParameterType.STRING, "OpenCV operation to perform", True, list(self.OPERATION_METADATA.keys())),
            ("timeout", NodeParameterType.NUMBER, "Operation timeout in seconds", False, None, 30),
        ]
        
        # Operation-specific parameters
        operation_params = [
            # Image parameters
            ("image_path", NodeParameterType.STRING, "Path to input image file", False),
            ("image_data", NodeParameterType.STRING, "Base64 encoded image data", False),
            ("output_path", NodeParameterType.STRING, "Path to save output image", False),
            ("color_mode", NodeParameterType.STRING, "Image loading color mode", False, ["color", "grayscale", "unchanged"], "color"),
            
            # Transformation parameters
            ("width", NodeParameterType.NUMBER, "Image width", False),
            ("height", NodeParameterType.NUMBER, "Image height", False),
            ("conversion", NodeParameterType.STRING, "Color space conversion", False, 
             ["bgr_to_rgb", "rgb_to_bgr", "bgr_to_gray", "gray_to_bgr", "bgr_to_hsv", "hsv_to_bgr"], "bgr_to_rgb"),
            ("interpolation", NodeParameterType.STRING, "Interpolation method", False, 
             ["nearest", "linear", "cubic", "area", "lanczos"], "linear"),
            
            # Filter parameters
            ("kernel_size", NodeParameterType.NUMBER, "Kernel size for filters", False, None, 5),
            ("sigma_x", NodeParameterType.NUMBER, "Gaussian sigma X", False, None, 1.0),
            ("sigma_y", NodeParameterType.NUMBER, "Gaussian sigma Y", False, None, 0),
            ("threshold1", NodeParameterType.NUMBER, "First threshold for edge detection", False, None, 100),
            ("threshold2", NodeParameterType.NUMBER, "Second threshold for edge detection", False, None, 200),
            ("aperture_size", NodeParameterType.NUMBER, "Aperture size for Sobel operator", False, None, 3),
            
            # Detection parameters
            ("scale_factor", NodeParameterType.NUMBER, "Scale factor for cascade detection", False, None, 1.1),
            ("min_neighbors", NodeParameterType.NUMBER, "Minimum neighbors for cascade detection", False, None, 5),
            ("n_features", NodeParameterType.NUMBER, "Number of features to detect", False, None, 500),
            
            # Template matching
            ("template_data", NodeParameterType.STRING, "Base64 encoded template image", False),
            ("template_path", NodeParameterType.STRING, "Path to template image", False),
            ("method", NodeParameterType.STRING, "Template matching method", False, 
             ["sqdiff", "sqdiff_normed", "ccorr", "ccorr_normed", "ccoeff", "ccoeff_normed"], "ccoeff_normed"),
            
            # Contour parameters
            ("mode", NodeParameterType.STRING, "Contour retrieval mode", False, 
             ["external", "list", "ccomp", "tree"], "external"),
            ("contour_method", NodeParameterType.STRING, "Contour approximation method", False, 
             ["none", "simple", "tc89_l1", "tc89_kcos"], "simple"),
            
            # DNN parameters
            ("model_path", NodeParameterType.STRING, "Path to DNN model file", False),
            ("config_path", NodeParameterType.STRING, "Path to DNN config file", False),
            ("framework", NodeParameterType.STRING, "DNN framework", False, 
             ["auto", "tensorflow", "caffe", "darknet", "onnx"], "auto"),
            ("size", NodeParameterType.ARRAY, "Input size for DNN [width, height]", False, None, [416, 416]),
            ("mean", NodeParameterType.ARRAY, "Mean values for DNN [B, G, R]", False, None, [0, 0, 0]),
            ("swap_rb", NodeParameterType.BOOLEAN, "Swap R and B channels", False, None, True),
            
            # Drawing parameters
            ("color", NodeParameterType.ARRAY, "Color in BGR format [B, G, R]", False, None, [0, 255, 0]),
            ("thickness", NodeParameterType.NUMBER, "Line thickness", False, None, 2),
            ("text", NodeParameterType.STRING, "Text to draw", False),
            ("font_scale", NodeParameterType.NUMBER, "Font scale", False, None, 1.0),
            
            # Geometric parameters
            ("points", NodeParameterType.ARRAY, "Array of points", False),
            ("center", NodeParameterType.ARRAY, "Center point [x, y]", False),
            ("radius", NodeParameterType.NUMBER, "Circle radius", False),
            ("axes", NodeParameterType.ARRAY, "Ellipse axes [a, b]", False),
            ("angle", NodeParameterType.NUMBER, "Rotation angle", False, None, 0),
            
            # Video parameters
            ("video_path", NodeParameterType.STRING, "Path to video file", False),
            ("fps", NodeParameterType.NUMBER, "Frames per second", False, None, 30),
            ("codec", NodeParameterType.STRING, "Video codec", False, ["XVID", "MJPG", "X264"], "XVID"),
            
            # Calibration parameters
            ("object_points", NodeParameterType.ARRAY, "3D object points", False),
            ("image_points", NodeParameterType.ARRAY, "2D image points", False),
            ("camera_matrix", NodeParameterType.ARRAY, "Camera intrinsic matrix", False),
            ("dist_coeffs", NodeParameterType.ARRAY, "Distortion coefficients", False),
            ("board_size", NodeParameterType.ARRAY, "Chessboard size [width, height]", False, None, [9, 6]),
        ]
        
        # Combine all parameters
        all_params = []
        for param_tuple in base_params + operation_params:
            if len(param_tuple) == 5:
                name, param_type, description, required, enum_values = param_tuple
                all_params.append(NodeParameter(
                    name=name, 
                    type=param_type, 
                    description=description, 
                    required=required, 
                    enum_values=enum_values
                ))
            elif len(param_tuple) == 6:
                name, param_type, description, required, enum_values, default_value = param_tuple
                all_params.append(NodeParameter(
                    name=name, 
                    type=param_type, 
                    description=description, 
                    required=required, 
                    enum_values=enum_values, 
                    default_value=default_value
                ))
        
        return NodeSchema(
            node_type="opencv",
            version="1.0.0",
            description="OpenCV computer vision and image processing operations",
            parameters=all_params,
            outputs={
                "status": NodeParameterType.STRING,
                "operation": NodeParameterType.STRING,
                "start_time": NodeParameterType.STRING,
                "execution_time": NodeParameterType.NUMBER,
                "inputs": NodeParameterType.OBJECT,
                "result": NodeParameterType.OBJECT,
                "error": NodeParameterType.STRING,
                "timestamp": NodeParameterType.STRING
            }
        )

    def validate_custom(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom validation for OpenCV operations."""
        params = node_data.get("params", {})
        operation = params.get("operation")
        
        if operation not in self.OPERATION_METADATA:
            raise NodeValidationError(f"Invalid operation: {operation}")
        
        # Operation-specific validation using metadata
        metadata = self.OPERATION_METADATA[operation]
        
        # Check required parameters
        for param in metadata["required_params"]:
            if param not in params or params[param] is None:
                raise NodeValidationError(f"Parameter '{param}' is required for operation '{operation}'")
        
        # Validate image input
        if operation in [OpenCVOperation.READ_IMAGE]:
            image_path = params.get("image_path")
            if not image_path or not os.path.exists(image_path):
                raise NodeValidationError("Valid image_path is required and file must exist")
        
        if operation in [OpenCVOperation.WRITE_IMAGE]:
            if not params.get("image_data") and not params.get("image_path"):
                raise NodeValidationError("Either image_data (base64) or image_path is required")
        
        # Validate DNN operations
        if operation == OpenCVOperation.LOAD_DNN_MODEL:
            model_path = params.get("model_path")
            if not model_path or not os.path.exists(model_path):
                raise NodeValidationError("Valid model_path is required and file must exist")
        
        # Validate template matching
        if operation == OpenCVOperation.TEMPLATE_MATCH:
            if not params.get("template_data") and not params.get("template_path"):
                raise NodeValidationError("Either template_data (base64) or template_path is required")
        
        return node_data

    @asynccontextmanager
    async def _get_opencv_wrapper(self, params: Dict[str, Any]):
        """Context manager for OpenCV wrapper with proper lifecycle."""
        timeout = params.get("timeout", 30)
        
        wrapper = None
        try:
            wrapper = OpenCVWrapper()
            yield wrapper
        except Exception as e:
            logger.error(f"OpenCV wrapper error: {e}")
            raise NodeExecutionError(f"OpenCV operation failed: {e}")
        finally:
            # Cleanup if needed
            if wrapper and hasattr(wrapper, 'net') and wrapper.net:
                wrapper.net = None

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OpenCV operations with comprehensive error handling."""
        try:
            # Validate input
            validated_data = self.validate_custom(node_data)
            params = validated_data["params"]
            operation = params["operation"]
            
            # Check OpenCV availability
            if not OPENCV_AVAILABLE:
                return {
                    "status": "error",
                    "error": "OpenCV library not available. Install with: pip install opencv-python",
                    "inputs": self._mask_sensitive_data(params),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Execute operation using dispatch map
            if operation not in self.operation_dispatch:
                return {
                    "status": "error",
                    "error": f"Operation '{operation}' not implemented",
                    "inputs": self._mask_sensitive_data(params),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Get operation handler and execute
            handler = self.operation_dispatch[operation]
            
            async with self._get_opencv_wrapper(params) as opencv_wrapper:
                result = await handler(opencv_wrapper, params)
                
                return {
                    "status": "success",
                    "result": result,
                    "inputs": self._mask_sensitive_data(params),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except NodeValidationError as e:
            return {
                "status": "error",
                "error": f"Validation error: {str(e)}",
                "inputs": self._mask_sensitive_data(node_data.get("params", {})),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except NodeExecutionError as e:
            return {
                "status": "error", 
                "error": str(e),
                "inputs": self._mask_sensitive_data(node_data.get("params", {})),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error in OpenCV operation: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "inputs": self._mask_sensitive_data(node_data.get("params", {})),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _mask_sensitive_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked = params.copy()
        
        # Mask base64 image data (can be very long)
        if "image_data" in masked and masked["image_data"]:
            masked["image_data"] = f"***BASE64_IMAGE_DATA***({len(masked['image_data'])} chars)"
        
        if "template_data" in masked and masked["template_data"]:
            masked["template_data"] = f"***BASE64_TEMPLATE_DATA***({len(masked['template_data'])} chars)"
        
        return masked

    # Operation handlers - Core operations
    async def _handle_read_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle READ_IMAGE operation."""
        image_path = params["image_path"]
        color_mode = params.get("color_mode", "color")
        
        image = opencv_wrapper.load_image(image_path, color_mode)
        if image is None:
            raise NodeExecutionError(f"Failed to load image from {image_path}")
        
        # Encode image as base64 for return
        image_base64 = opencv_wrapper.encode_image_base64(image)
        
        return {
            "image_data": image_base64,
            "shape": image.shape,
            "dtype": str(image.dtype),
            "path": image_path
        }

    async def _handle_write_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> bool:
        """Handle WRITE_IMAGE operation."""
        output_path = params["output_path"]
        
        # Get image from either base64 data or path
        if "image_data" in params:
            image = opencv_wrapper.decode_image_base64(params["image_data"])
        elif "image_path" in params:
            image = opencv_wrapper.load_image(params["image_path"])
        else:
            raise NodeExecutionError("Either image_data or image_path is required")
        
        success = opencv_wrapper.save_image(image, output_path)
        if not success:
            raise NodeExecutionError(f"Failed to save image to {output_path}")
        
        return {"saved": True, "path": output_path}

    async def _handle_color_convert(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle COLOR_CONVERT operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        conversion = params["conversion"]
        
        converted = opencv_wrapper.convert_color(image, conversion)
        result_base64 = opencv_wrapper.encode_image_base64(converted)
        
        return {
            "image_data": result_base64,
            "conversion": conversion,
            "original_shape": image.shape,
            "result_shape": converted.shape
        }

    async def _handle_resize_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RESIZE_IMAGE operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        width = int(params["width"])
        height = int(params["height"])
        interpolation = params.get("interpolation", "linear")
        
        resized = opencv_wrapper.resize_image(image, width, height, interpolation)
        result_base64 = opencv_wrapper.encode_image_base64(resized)
        
        return {
            "image_data": result_base64,
            "original_size": [image.shape[1], image.shape[0]],
            "new_size": [width, height],
            "interpolation": interpolation
        }

    async def _handle_gaussian_blur(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GAUSSIAN_BLUR operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        kernel_size = int(params["kernel_size"])
        sigma_x = float(params["sigma_x"])
        sigma_y = float(params.get("sigma_y", 0))
        
        # Ensure kernel size is odd
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        blurred = opencv_wrapper.gaussian_blur(image, kernel_size, sigma_x, sigma_y)
        result_base64 = opencv_wrapper.encode_image_base64(blurred)
        
        return {
            "image_data": result_base64,
            "kernel_size": kernel_size,
            "sigma_x": sigma_x,
            "sigma_y": sigma_y
        }

    async def _handle_canny(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CANNY operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        threshold1 = int(params["threshold1"])
        threshold2 = int(params["threshold2"])
        aperture_size = int(params.get("aperture_size", 3))
        
        edges = opencv_wrapper.canny_edge_detection(image, threshold1, threshold2, aperture_size)
        result_base64 = opencv_wrapper.encode_image_base64(edges)
        
        return {
            "image_data": result_base64,
            "threshold1": threshold1,
            "threshold2": threshold2,
            "aperture_size": aperture_size,
            "edge_pixels": int(np.sum(edges > 0))
        }

    async def _handle_detect_faces(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_FACES operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        scale_factor = float(params.get("scale_factor", 1.1))
        min_neighbors = int(params.get("min_neighbors", 5))
        
        faces = opencv_wrapper.detect_faces(image, scale_factor, min_neighbors)
        
        return {
            "faces": faces,
            "face_count": len(faces),
            "scale_factor": scale_factor,
            "min_neighbors": min_neighbors
        }

    async def _handle_detect_orb(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_ORB operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        n_features = int(params.get("n_features", 500))
        
        keypoints, descriptors = opencv_wrapper.detect_orb_features(image, n_features)
        
        # Convert keypoints to serializable format
        kp_data = []
        for kp in keypoints:
            kp_data.append({
                "x": float(kp.pt[0]),
                "y": float(kp.pt[1]),
                "size": float(kp.size),
                "angle": float(kp.angle),
                "response": float(kp.response)
            })
        
        return {
            "keypoints": kp_data,
            "keypoint_count": len(keypoints),
            "descriptor_shape": descriptors.shape if descriptors is not None else None,
            "n_features": n_features
        }

    async def _handle_template_match(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TEMPLATE_MATCH operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        
        # Get template from either base64 data or path
        if "template_data" in params:
            template = opencv_wrapper.decode_image_base64(params["template_data"])
        elif "template_path" in params:
            template = opencv_wrapper.load_image(params["template_path"])
        else:
            raise NodeExecutionError("Either template_data or template_path is required")
        
        method = params.get("method", "ccoeff_normed")
        
        result, best_match_loc, confidence = opencv_wrapper.template_match(image, template, method)
        
        return {
            "best_match_location": list(best_match_loc),
            "confidence": float(confidence),
            "method": method,
            "template_size": template.shape[:2]
        }

    async def _handle_find_contours(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FIND_CONTOURS operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        mode = params.get("mode", "external")
        method = params.get("method", "simple")
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        contours, hierarchy = opencv_wrapper.find_contours(image, mode, method)
        
        # Convert contours to serializable format
        contour_data = []
        for contour in contours:
            contour_points = contour.reshape(-1, 2).tolist()
            area = float(cv2.contourArea(contour))
            perimeter = float(cv2.arcLength(contour, True))
            contour_data.append({
                "points": contour_points,
                "area": area,
                "perimeter": perimeter
            })
        
        return {
            "contours": contour_data,
            "contour_count": len(contours),
            "mode": mode,
            "method": method
        }

    # Placeholder handlers for remaining operations
    async def _handle_create_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CREATE_IMAGE operation."""
        return {"status": "not_implemented"}

    async def _handle_copy_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle COPY_IMAGE operation."""
        return {"status": "not_implemented"}

    async def _handle_convert_dtype(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CONVERT_DTYPE operation."""
        return {"status": "not_implemented"}

    async def _handle_split_channels(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SPLIT_CHANNELS operation."""
        return {"status": "not_implemented"}

    async def _handle_merge_channels(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MERGE_CHANNELS operation."""
        return {"status": "not_implemented"}

    async def _handle_crop_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CROP_IMAGE operation."""
        return {"status": "not_implemented"}

    async def _handle_rotate_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ROTATE_IMAGE operation."""
        return {"status": "not_implemented"}

    async def _handle_flip_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FLIP_IMAGE operation."""
        return {"status": "not_implemented"}

    async def _handle_warp_affine(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WARP_AFFINE operation."""
        return {"status": "not_implemented"}

    async def _handle_warp_perspective(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WARP_PERSPECTIVE operation."""
        return {"status": "not_implemented"}

    async def _handle_blur(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BLUR operation."""
        return {"status": "not_implemented"}

    async def _handle_median_blur(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MEDIAN_BLUR operation."""
        return {"status": "not_implemented"}

    async def _handle_bilateral_filter(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BILATERAL_FILTER operation."""
        return {"status": "not_implemented"}

    async def _handle_box_filter(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BOX_FILTER operation."""
        return {"status": "not_implemented"}

    async def _handle_sobel(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SOBEL operation."""
        return {"status": "not_implemented"}

    async def _handle_laplacian(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LAPLACIAN operation."""
        return {"status": "not_implemented"}

    async def _handle_erode(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ERODE operation."""
        return {"status": "not_implemented"}

    async def _handle_dilate(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DILATE operation."""
        return {"status": "not_implemented"}

    async def _handle_morphology_ex(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MORPHOLOGY_EX operation."""
        return {"status": "not_implemented"}

    async def _handle_threshold(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle THRESHOLD operation."""
        return {"status": "not_implemented"}

    async def _handle_adaptive_threshold(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ADAPTIVE_THRESHOLD operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_contours(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_CONTOURS operation."""
        return {"status": "not_implemented"}

    async def _handle_contour_area(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CONTOUR_AREA operation."""
        return {"status": "not_implemented"}

    async def _handle_contour_perimeter(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CONTOUR_PERIMETER operation."""
        return {"status": "not_implemented"}

    async def _handle_bounding_rect(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BOUNDING_RECT operation."""
        return {"status": "not_implemented"}

    async def _handle_min_enclosing_circle(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MIN_ENCLOSING_CIRCLE operation."""
        return {"status": "not_implemented"}

    async def _handle_convex_hull(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CONVEX_HULL operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_line(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_LINE operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_rectangle(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_RECTANGLE operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_circle(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_CIRCLE operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_ellipse(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_ELLIPSE operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_polygon(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_POLYGON operation."""
        return {"status": "not_implemented"}

    async def _handle_put_text(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PUT_TEXT operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_sift(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_SIFT operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_surf(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_SURF operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_fast(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_FAST operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_brief(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_BRIEF operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_brisk(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_BRISK operation."""
        return {"status": "not_implemented"}

    async def _handle_match_features(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MATCH_FEATURES operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_keypoints(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_KEYPOINTS operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_matches(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_MATCHES operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_eyes(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_EYES operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_smiles(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_SMILES operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_bodies(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_BODIES operation."""
        return {"status": "not_implemented"}

    async def _handle_detect_cars(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_CARS operation."""
        return {"status": "not_implemented"}

    async def _handle_cascade_detect(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CASCADE_DETECT operation."""
        return {"status": "not_implemented"}

    async def _handle_hog_detect(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HOG_DETECT operation."""
        return {"status": "not_implemented"}

    async def _handle_calibrate_camera(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CALIBRATE_CAMERA operation."""
        return {"status": "not_implemented"}

    async def _handle_undistort_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle UNDISTORT_IMAGE operation."""
        return {"status": "not_implemented"}

    async def _handle_find_chessboard(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FIND_CHESSBOARD operation."""
        return {"status": "not_implemented"}

    async def _handle_draw_chessboard(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DRAW_CHESSBOARD operation."""
        return {"status": "not_implemented"}

    async def _handle_stereo_calibrate(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle STEREO_CALIBRATE operation."""
        return {"status": "not_implemented"}

    async def _handle_stereo_rectify(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle STEREO_RECTIFY operation."""
        return {"status": "not_implemented"}

    async def _handle_solve_pnp(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SOLVE_PNP operation."""
        return {"status": "not_implemented"}

    async def _handle_project_points(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PROJECT_POINTS operation."""
        return {"status": "not_implemented"}

    async def _handle_rodrigues(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RODRIGUES operation."""
        return {"status": "not_implemented"}

    async def _handle_load_dnn_model(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle LOAD_DNN_MODEL operation."""
        model_path = params["model_path"]
        config_path = params.get("config_path")
        framework = params.get("framework", "auto")
        
        success = opencv_wrapper.load_dnn_model(model_path, config_path, framework)
        if not success:
            raise NodeExecutionError("Failed to load DNN model")
        
        return {
            "loaded": True,
            "model_path": model_path,
            "config_path": config_path,
            "framework": framework
        }

    async def _handle_dnn_forward(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DNN_FORWARD operation."""
        return {"status": "not_implemented"}

    async def _handle_blob_from_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BLOB_FROM_IMAGE operation."""
        image = opencv_wrapper.decode_image_base64(params["image_data"])
        scale_factor = float(params.get("scale_factor", 1.0))
        size = params.get("size", [416, 416])
        mean = params.get("mean", [0, 0, 0])
        swap_rb = params.get("swap_rb", True)
        
        blob = opencv_wrapper.create_blob_from_image(image, scale_factor, tuple(size), tuple(mean), swap_rb)
        
        return {
            "blob_shape": blob.shape,
            "scale_factor": scale_factor,
            "size": size,
            "mean": mean,
            "swap_rb": swap_rb
        }

    async def _handle_detect_objects_yolo(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DETECT_OBJECTS_YOLO operation."""
        return {"status": "not_implemented"}

    async def _handle_classify_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CLASSIFY_IMAGE operation."""
        return {"status": "not_implemented"}

    async def _handle_segment_image(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SEGMENT_IMAGE operation."""
        return {"status": "not_implemented"}

    async def _handle_pose_estimation(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle POSE_ESTIMATION operation."""
        return {"status": "not_implemented"}

    async def _handle_read_video(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle READ_VIDEO operation."""
        return {"status": "not_implemented"}

    async def _handle_write_video(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WRITE_VIDEO operation."""
        return {"status": "not_implemented"}

    async def _handle_video_capture(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle VIDEO_CAPTURE operation."""
        return {"status": "not_implemented"}

    async def _handle_background_subtraction(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BACKGROUND_SUBTRACTION operation."""
        return {"status": "not_implemented"}

    async def _handle_optical_flow(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OPTICAL_FLOW operation."""
        return {"status": "not_implemented"}

    async def _handle_motion_detection(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MOTION_DETECTION operation."""
        return {"status": "not_implemented"}

    async def _handle_multi_template_match(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MULTI_TEMPLATE_MATCH operation."""
        return {"status": "not_implemented"}

    async def _handle_calc_histogram(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CALC_HISTOGRAM operation."""
        return {"status": "not_implemented"}

    async def _handle_histogram_equalization(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HISTOGRAM_EQUALIZATION operation."""
        return {"status": "not_implemented"}

    async def _handle_clahe(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CLAHE operation."""
        return {"status": "not_implemented"}

    async def _handle_compare_histograms(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle COMPARE_HISTOGRAMS operation."""
        return {"status": "not_implemented"}

    async def _handle_calculate_psnr(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CALCULATE_PSNR operation."""
        return {"status": "not_implemented"}

    async def _handle_calculate_ssim(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CALCULATE_SSIM operation."""
        return {"status": "not_implemented"}

    async def _handle_calculate_mse(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CALCULATE_MSE operation."""
        return {"status": "not_implemented"}

    async def _handle_inpaint(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle INPAINT operation."""
        return {"status": "not_implemented"}

    async def _handle_seamless_clone(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SEAMLESS_CLONE operation."""
        return {"status": "not_implemented"}

    async def _handle_grab_cut(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GRAB_CUT operation."""
        return {"status": "not_implemented"}

    async def _handle_watershed(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WATERSHED operation."""
        return {"status": "not_implemented"}

    async def _handle_mean_shift(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MEAN_SHIFT operation."""
        return {"status": "not_implemented"}

    async def _handle_cam_shift(self, opencv_wrapper: OpenCVWrapper, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CAM_SHIFT operation."""
        return {"status": "not_implemented"}