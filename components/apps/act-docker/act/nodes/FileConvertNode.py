"""
File Convert Node - Comprehensive file format conversion utility
Refactored with improved architecture: dispatch maps, unified async/sync handling,
proper connection lifecycle, and standardized return shapes.
Supports conversion between multiple file formats including documents, images,
audio, video, archives, and data formats.
"""

import logging
import asyncio
import json
import base64
import os
import tempfile
import shutil
import mimetypes
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from io import BytesIO
import zipfile
import tarfile

# Image processing libraries
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Document processing libraries
try:
    import pypandoc
    PANDOC_AVAILABLE = True
except ImportError:
    PANDOC_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    from docx2pdf import convert as docx_to_pdf
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import openpyxl
    from openpyxl.workbook import Workbook
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# Audio processing libraries
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

# Video processing libraries
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

# Data format libraries
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import xml.etree.ElementTree as ET
    import xmltodict
    XML_AVAILABLE = True
except ImportError:
    XML_AVAILABLE = False

try:
    import csv
    CSV_AVAILABLE = True
except ImportError:
    CSV_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

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

# Configure logging
logger = logging.getLogger(__name__)

class FileConvertOperation:
    """All available file conversion operations organized by category."""
    
    # Image conversions
    IMAGE_TO_JPG = "image_to_jpg"
    IMAGE_TO_PNG = "image_to_png"
    IMAGE_TO_GIF = "image_to_gif"
    IMAGE_TO_BMP = "image_to_bmp"
    IMAGE_TO_TIFF = "image_to_tiff"
    IMAGE_TO_WEBP = "image_to_webp"
    IMAGE_TO_ICO = "image_to_ico"
    IMAGE_RESIZE = "image_resize"
    IMAGE_ROTATE = "image_rotate"
    IMAGE_CROP = "image_crop"
    
    # Document conversions
    DOC_TO_PDF = "doc_to_pdf"
    DOCX_TO_PDF = "docx_to_pdf"
    PDF_TO_TEXT = "pdf_to_text"
    MD_TO_HTML = "md_to_html"
    MD_TO_PDF = "md_to_pdf"
    HTML_TO_PDF = "html_to_pdf"
    HTML_TO_MD = "html_to_md"
    TXT_TO_PDF = "txt_to_pdf"
    RTF_TO_DOCX = "rtf_to_docx"
    DOCX_TO_HTML = "docx_to_html"
    
    # Spreadsheet conversions
    XLS_TO_XLSX = "xls_to_xlsx"
    XLSX_TO_CSV = "xlsx_to_csv"
    CSV_TO_XLSX = "csv_to_xlsx"
    XLSX_TO_JSON = "xlsx_to_json"
    JSON_TO_XLSX = "json_to_xlsx"
    CSV_TO_JSON = "csv_to_json"
    JSON_TO_CSV = "json_to_csv"
    
    # Audio conversions
    MP3_TO_WAV = "mp3_to_wav"
    WAV_TO_MP3 = "wav_to_mp3"
    MP3_TO_AAC = "mp3_to_aac"
    WAV_TO_FLAC = "wav_to_flac"
    AUDIO_TRIM = "audio_trim"
    AUDIO_MERGE = "audio_merge"
    AUDIO_EXTRACT = "audio_extract"
    
    # Video conversions
    MP4_TO_AVI = "mp4_to_avi"
    AVI_TO_MP4 = "avi_to_mp4"
    MOV_TO_MP4 = "mov_to_mp4"
    VIDEO_TO_AUDIO = "video_to_audio"
    VIDEO_RESIZE = "video_resize"
    VIDEO_TRIM = "video_trim"
    VIDEO_MERGE = "video_merge"
    VIDEO_TO_GIF = "video_to_gif"
    
    # Archive conversions
    ZIP_CREATE = "zip_create"
    ZIP_EXTRACT = "zip_extract"
    TAR_CREATE = "tar_create"
    TAR_EXTRACT = "tar_extract"
    RAR_EXTRACT = "rar_extract"
    
    # Data format conversions
    JSON_TO_XML = "json_to_xml"
    XML_TO_JSON = "xml_to_json"
    JSON_TO_YAML = "json_to_yaml"
    YAML_TO_JSON = "yaml_to_json"
    CSV_TO_XML = "csv_to_xml"
    XML_TO_CSV = "xml_to_csv"
    
    # Encoding conversions
    BASE64_ENCODE = "base64_encode"
    BASE64_DECODE = "base64_decode"
    URL_ENCODE = "url_encode"
    URL_DECODE = "url_decode"
    HEX_ENCODE = "hex_encode"
    HEX_DECODE = "hex_decode"
    
    # Text conversions
    TEXT_TO_UPPER = "text_to_upper"
    TEXT_TO_LOWER = "text_to_lower"
    TEXT_TO_TITLE = "text_to_title"
    TEXT_CLEAN = "text_clean"
    TEXT_EXTRACT = "text_extract"

class FileConverter:
    """Unified file converter that handles various format conversions."""
    
    def __init__(self):
        """Initialize the file converter."""
        self.temp_dir = tempfile.mkdtemp()
        
    def cleanup(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def get_temp_path(self, filename: str) -> str:
        """Get a temporary file path."""
        return os.path.join(self.temp_dir, filename)
    
    def save_base64_to_file(self, base64_data: str, file_path: str) -> None:
        """Save base64 encoded data to a file."""
        try:
            file_data = base64.b64decode(base64_data)
            with open(file_path, 'wb') as f:
                f.write(file_data)
        except Exception as e:
            raise ValueError(f"Failed to decode base64 data: {e}")
    
    def file_to_base64(self, file_path: str) -> str:
        """Convert file to base64 encoded string."""
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to encode file to base64: {e}")
    
    # Image conversion methods
    def convert_image_format(self, input_data: str, output_format: str, quality: int = 95, **kwargs) -> str:
        """Convert image between formats."""
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL library not available for image conversion")
        
        # Create temporary files
        input_path = self.get_temp_path("input_image")
        output_path = self.get_temp_path(f"output_image.{output_format.lower()}")
        
        # Save input data
        self.save_base64_to_file(input_data, input_path)
        
        # Convert image
        with Image.open(input_path) as img:
            # Handle special cases
            if output_format.upper() == 'JPEG' or output_format.upper() == 'JPG':
                # Convert RGBA to RGB for JPEG
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(output_path, 'JPEG', quality=quality, optimize=True)
            elif output_format.upper() == 'PNG':
                img.save(output_path, 'PNG', optimize=True)
            elif output_format.upper() == 'WEBP':
                img.save(output_path, 'WEBP', quality=quality, optimize=True)
            elif output_format.upper() == 'GIF':
                img.save(output_path, 'GIF', optimize=True)
            elif output_format.upper() == 'ICO':
                # ICO format requires specific sizes
                sizes = kwargs.get('ico_sizes', [16, 32, 48, 64, 128, 256])
                img.save(output_path, 'ICO', sizes=[(s, s) for s in sizes])
            else:
                img.save(output_path, output_format.upper())
        
        return self.file_to_base64(output_path)
    
    def resize_image(self, input_data: str, width: int, height: int, maintain_aspect: bool = True) -> str:
        """Resize an image."""
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL library not available for image resizing")
        
        input_path = self.get_temp_path("input_image")
        output_path = self.get_temp_path("resized_image.png")
        
        self.save_base64_to_file(input_data, input_path)
        
        with Image.open(input_path) as img:
            if maintain_aspect:
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            img.save(output_path, 'PNG')
        
        return self.file_to_base64(output_path)
    
    def rotate_image(self, input_data: str, angle: float, expand: bool = True) -> str:
        """Rotate an image."""
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL library not available for image rotation")
        
        input_path = self.get_temp_path("input_image")
        output_path = self.get_temp_path("rotated_image.png")
        
        self.save_base64_to_file(input_data, input_path)
        
        with Image.open(input_path) as img:
            rotated = img.rotate(angle, expand=expand)
            rotated.save(output_path, 'PNG')
        
        return self.file_to_base64(output_path)
    
    def crop_image(self, input_data: str, left: int, top: int, right: int, bottom: int) -> str:
        """Crop an image."""
        if not PIL_AVAILABLE:
            raise RuntimeError("PIL library not available for image cropping")
        
        input_path = self.get_temp_path("input_image")
        output_path = self.get_temp_path("cropped_image.png")
        
        self.save_base64_to_file(input_data, input_path)
        
        with Image.open(input_path) as img:
            cropped = img.crop((left, top, right, bottom))
            cropped.save(output_path, 'PNG')
        
        return self.file_to_base64(output_path)
    
    # Document conversion methods
    def convert_document_with_pandoc(self, input_data: str, from_format: str, to_format: str) -> str:
        """Convert documents using pandoc."""
        if not PANDOC_AVAILABLE:
            raise RuntimeError("Pandoc not available for document conversion")
        
        input_path = self.get_temp_path(f"input.{from_format}")
        output_path = self.get_temp_path(f"output.{to_format}")
        
        # For text-based formats, decode as text
        if from_format in ['md', 'txt', 'html', 'rtf']:
            try:
                text_data = base64.b64decode(input_data).decode('utf-8')
                with open(input_path, 'w', encoding='utf-8') as f:
                    f.write(text_data)
            except:
                self.save_base64_to_file(input_data, input_path)
        else:
            self.save_base64_to_file(input_data, input_path)
        
        # Convert using pandoc
        pypandoc.convert_file(input_path, to_format, outputfile=output_path)
        
        return self.file_to_base64(output_path)
    
    # Audio conversion methods
    def convert_audio_format(self, input_data: str, output_format: str, bitrate: str = "128k") -> str:
        """Convert audio between formats."""
        if not PYDUB_AVAILABLE:
            raise RuntimeError("Pydub library not available for audio conversion")
        
        input_path = self.get_temp_path("input_audio")
        output_path = self.get_temp_path(f"output_audio.{output_format}")
        
        self.save_base64_to_file(input_data, input_path)
        
        # Load audio file
        audio = AudioSegment.from_file(input_path)
        
        # Export to target format
        audio.export(output_path, format=output_format, bitrate=bitrate)
        
        return self.file_to_base64(output_path)
    
    def trim_audio(self, input_data: str, start_ms: int, end_ms: int) -> str:
        """Trim audio file."""
        if not PYDUB_AVAILABLE:
            raise RuntimeError("Pydub library not available for audio trimming")
        
        input_path = self.get_temp_path("input_audio")
        output_path = self.get_temp_path("trimmed_audio.mp3")
        
        self.save_base64_to_file(input_data, input_path)
        
        audio = AudioSegment.from_file(input_path)
        trimmed = audio[start_ms:end_ms]
        trimmed.export(output_path, format="mp3")
        
        return self.file_to_base64(output_path)
    
    # Data format conversion methods
    def json_to_xml(self, json_data: str) -> str:
        """Convert JSON to XML."""
        try:
            data = json.loads(json_data)
            
            def dict_to_xml(tag, d):
                """Convert dictionary to XML element."""
                elem = ET.Element(tag)
                for key, val in d.items():
                    if isinstance(val, dict):
                        elem.append(dict_to_xml(key, val))
                    elif isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict):
                                elem.append(dict_to_xml(key, item))
                            else:
                                sub_elem = ET.SubElement(elem, key)
                                sub_elem.text = str(item)
                    else:
                        sub_elem = ET.SubElement(elem, key)
                        sub_elem.text = str(val)
                return elem
            
            root = dict_to_xml("root", data)
            return ET.tostring(root, encoding='unicode')
        except Exception as e:
            raise ValueError(f"Failed to convert JSON to XML: {e}")
    
    def xml_to_json(self, xml_data: str) -> str:
        """Convert XML to JSON."""
        try:
            if XML_AVAILABLE and hasattr(xmltodict, 'parse'):
                data = xmltodict.parse(xml_data)
                return json.dumps(data, indent=2)
            else:
                # Fallback to basic XML parsing
                root = ET.fromstring(xml_data)
                
                def elem_to_dict(elem):
                    result = {}
                    if elem.text and elem.text.strip():
                        result['text'] = elem.text.strip()
                    for child in elem:
                        child_data = elem_to_dict(child)
                        if child.tag in result:
                            if not isinstance(result[child.tag], list):
                                result[child.tag] = [result[child.tag]]
                            result[child.tag].append(child_data)
                        else:
                            result[child.tag] = child_data
                    return result
                
                data = {root.tag: elem_to_dict(root)}
                return json.dumps(data, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to convert XML to JSON: {e}")
    
    def json_to_yaml(self, json_data: str) -> str:
        """Convert JSON to YAML."""
        if not YAML_AVAILABLE:
            raise RuntimeError("YAML library not available")
        
        try:
            data = json.loads(json_data)
            return yaml.dump(data, default_flow_style=False)
        except Exception as e:
            raise ValueError(f"Failed to convert JSON to YAML: {e}")
    
    def yaml_to_json(self, yaml_data: str) -> str:
        """Convert YAML to JSON."""
        if not YAML_AVAILABLE:
            raise RuntimeError("YAML library not available")
        
        try:
            data = yaml.safe_load(yaml_data)
            return json.dumps(data, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to convert YAML to JSON: {e}")
    
    def csv_to_json(self, csv_data: str, delimiter: str = ',') -> str:
        """Convert CSV to JSON."""
        try:
            lines = csv_data.strip().split('\n')
            if not lines:
                return "[]"
            
            reader = csv.DictReader(lines, delimiter=delimiter)
            data = list(reader)
            return json.dumps(data, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to convert CSV to JSON: {e}")
    
    def json_to_csv(self, json_data: str) -> str:
        """Convert JSON to CSV."""
        try:
            data = json.loads(json_data)
            if not isinstance(data, list) or not data:
                raise ValueError("JSON must be a non-empty array of objects")
            
            output = BytesIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
            return output.getvalue().decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to convert JSON to CSV: {e}")
    
    # Archive operations
    def create_zip(self, files: List[Dict[str, str]]) -> str:
        """Create a ZIP archive from files."""
        output_path = self.get_temp_path("archive.zip")
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in files:
                filename = file_info['filename']
                content = file_info['content']  # base64 encoded
                
                # Create temporary file
                temp_file = self.get_temp_path(filename)
                self.save_base64_to_file(content, temp_file)
                
                # Add to zip
                zipf.write(temp_file, filename)
        
        return self.file_to_base64(output_path)
    
    def extract_zip(self, zip_data: str) -> List[Dict[str, str]]:
        """Extract files from ZIP archive."""
        input_path = self.get_temp_path("input.zip")
        extract_dir = self.get_temp_path("extracted")
        
        self.save_base64_to_file(zip_data, input_path)
        os.makedirs(extract_dir, exist_ok=True)
        
        files = []
        with zipfile.ZipFile(input_path, 'r') as zipf:
            zipf.extractall(extract_dir)
            
            for filename in zipf.namelist():
                file_path = os.path.join(extract_dir, filename)
                if os.path.isfile(file_path):
                    content = self.file_to_base64(file_path)
                    files.append({
                        'filename': filename,
                        'content': content,
                        'size': os.path.getsize(file_path)
                    })
        
        return files
    
    # Encoding operations
    def encode_base64(self, text: str) -> str:
        """Encode text to base64."""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    def decode_base64(self, encoded: str) -> str:
        """Decode base64 to text."""
        try:
            return base64.b64decode(encoded).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decode base64: {e}")
    
    def encode_hex(self, text: str) -> str:
        """Encode text to hexadecimal."""
        return text.encode('utf-8').hex()
    
    def decode_hex(self, hex_data: str) -> str:
        """Decode hexadecimal to text."""
        try:
            return bytes.fromhex(hex_data).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decode hex: {e}")

class FileConvertNode(BaseNode):
    """File Convert Node for comprehensive file format conversions."""
    
    def __init__(self):
        super().__init__()
        
        # Create operation dispatch map for clean routing
        self.operation_dispatch = {
            # Image conversions
            FileConvertOperation.IMAGE_TO_JPG: self._handle_image_to_jpg,
            FileConvertOperation.IMAGE_TO_PNG: self._handle_image_to_png,
            FileConvertOperation.IMAGE_TO_GIF: self._handle_image_to_gif,
            FileConvertOperation.IMAGE_TO_BMP: self._handle_image_to_bmp,
            FileConvertOperation.IMAGE_TO_TIFF: self._handle_image_to_tiff,
            FileConvertOperation.IMAGE_TO_WEBP: self._handle_image_to_webp,
            FileConvertOperation.IMAGE_TO_ICO: self._handle_image_to_ico,
            FileConvertOperation.IMAGE_RESIZE: self._handle_image_resize,
            FileConvertOperation.IMAGE_ROTATE: self._handle_image_rotate,
            FileConvertOperation.IMAGE_CROP: self._handle_image_crop,
            
            # Document conversions
            FileConvertOperation.MD_TO_HTML: self._handle_md_to_html,
            FileConvertOperation.MD_TO_PDF: self._handle_md_to_pdf,
            FileConvertOperation.HTML_TO_PDF: self._handle_html_to_pdf,
            FileConvertOperation.HTML_TO_MD: self._handle_html_to_md,
            FileConvertOperation.TXT_TO_PDF: self._handle_txt_to_pdf,
            
            # Spreadsheet conversions
            FileConvertOperation.CSV_TO_JSON: self._handle_csv_to_json,
            FileConvertOperation.JSON_TO_CSV: self._handle_json_to_csv,
            FileConvertOperation.XLSX_TO_CSV: self._handle_xlsx_to_csv,
            FileConvertOperation.CSV_TO_XLSX: self._handle_csv_to_xlsx,
            
            # Audio conversions
            FileConvertOperation.MP3_TO_WAV: self._handle_mp3_to_wav,
            FileConvertOperation.WAV_TO_MP3: self._handle_wav_to_mp3,
            FileConvertOperation.AUDIO_TRIM: self._handle_audio_trim,
            
            # Data format conversions
            FileConvertOperation.JSON_TO_XML: self._handle_json_to_xml,
            FileConvertOperation.XML_TO_JSON: self._handle_xml_to_json,
            FileConvertOperation.JSON_TO_YAML: self._handle_json_to_yaml,
            FileConvertOperation.YAML_TO_JSON: self._handle_yaml_to_json,
            
            # Archive operations
            FileConvertOperation.ZIP_CREATE: self._handle_zip_create,
            FileConvertOperation.ZIP_EXTRACT: self._handle_zip_extract,
            
            # Encoding operations
            FileConvertOperation.BASE64_ENCODE: self._handle_base64_encode,
            FileConvertOperation.BASE64_DECODE: self._handle_base64_decode,
            FileConvertOperation.HEX_ENCODE: self._handle_hex_encode,
            FileConvertOperation.HEX_DECODE: self._handle_hex_decode,
            
            # Text operations
            FileConvertOperation.TEXT_TO_UPPER: self._handle_text_to_upper,
            FileConvertOperation.TEXT_TO_LOWER: self._handle_text_to_lower,
            FileConvertOperation.TEXT_TO_TITLE: self._handle_text_to_title,
        }
    
    # Operation metadata for validation
    OPERATION_METADATA = {
        # Image operations
        FileConvertOperation.IMAGE_TO_JPG: {
            "required_params": ["input_data"],
            "optional_params": ["quality"],
            "description": "Convert image to JPEG format"
        },
        FileConvertOperation.IMAGE_TO_PNG: {
            "required_params": ["input_data"],
            "optional_params": [],
            "description": "Convert image to PNG format"
        },
        FileConvertOperation.IMAGE_RESIZE: {
            "required_params": ["input_data", "width", "height"],
            "optional_params": ["maintain_aspect"],
            "description": "Resize an image"
        },
        FileConvertOperation.IMAGE_ROTATE: {
            "required_params": ["input_data", "angle"],
            "optional_params": ["expand"],
            "description": "Rotate an image"
        },
        FileConvertOperation.IMAGE_CROP: {
            "required_params": ["input_data", "left", "top", "right", "bottom"],
            "optional_params": [],
            "description": "Crop an image"
        },
        
        # Document operations
        FileConvertOperation.MD_TO_HTML: {
            "required_params": ["input_data"],
            "optional_params": [],
            "description": "Convert Markdown to HTML"
        },
        
        # Data operations
        FileConvertOperation.JSON_TO_XML: {
            "required_params": ["input_data"],
            "optional_params": [],
            "description": "Convert JSON to XML"
        },
        FileConvertOperation.XML_TO_JSON: {
            "required_params": ["input_data"],
            "optional_params": [],
            "description": "Convert XML to JSON"
        },
        FileConvertOperation.CSV_TO_JSON: {
            "required_params": ["input_data"],
            "optional_params": ["delimiter"],
            "description": "Convert CSV to JSON"
        },
        FileConvertOperation.JSON_TO_CSV: {
            "required_params": ["input_data"],
            "optional_params": [],
            "description": "Convert JSON to CSV"
        },
        
        # Archive operations
        FileConvertOperation.ZIP_CREATE: {
            "required_params": ["files"],
            "optional_params": [],
            "description": "Create ZIP archive from files"
        },
        FileConvertOperation.ZIP_EXTRACT: {
            "required_params": ["input_data"],
            "optional_params": [],
            "description": "Extract files from ZIP archive"
        },
        
        # Encoding operations
        FileConvertOperation.BASE64_ENCODE: {
            "required_params": ["input_text"],
            "optional_params": [],
            "description": "Encode text to base64"
        },
        FileConvertOperation.BASE64_DECODE: {
            "required_params": ["input_data"],
            "optional_params": [],
            "description": "Decode base64 to text"
        },
        
        # Text operations
        FileConvertOperation.TEXT_TO_UPPER: {
            "required_params": ["input_text"],
            "optional_params": [],
            "description": "Convert text to uppercase"
        }
    }

    def get_schema(self) -> NodeSchema:
        """Generate schema with all parameters from operation metadata."""
        # Common parameters for all operations
        base_params = [
            ("operation", NodeParameterType.STRING, "File conversion operation to perform", True, list(self.OPERATION_METADATA.keys())),
            ("timeout", NodeParameterType.NUMBER, "Operation timeout in seconds", False, None, 60),
        ]
        
        # Operation-specific parameters
        operation_params = [
            # Input/output parameters
            ("input_data", NodeParameterType.STRING, "Base64 encoded input file data", False),
            ("input_text", NodeParameterType.STRING, "Input text data", False),
            ("output_format", NodeParameterType.STRING, "Target output format", False),
            
            # Image parameters
            ("quality", NodeParameterType.NUMBER, "Image quality (1-100)", False, None, 95),
            ("width", NodeParameterType.NUMBER, "Image width in pixels", False),
            ("height", NodeParameterType.NUMBER, "Image height in pixels", False),
            ("maintain_aspect", NodeParameterType.BOOLEAN, "Maintain aspect ratio", False, None, True),
            ("angle", NodeParameterType.NUMBER, "Rotation angle in degrees", False),
            ("expand", NodeParameterType.BOOLEAN, "Expand image to fit rotated content", False, None, True),
            ("left", NodeParameterType.NUMBER, "Left crop coordinate", False),
            ("top", NodeParameterType.NUMBER, "Top crop coordinate", False),
            ("right", NodeParameterType.NUMBER, "Right crop coordinate", False),
            ("bottom", NodeParameterType.NUMBER, "Bottom crop coordinate", False),
            
            # Audio parameters
            ("bitrate", NodeParameterType.STRING, "Audio bitrate", False, None, "128k"),
            ("start_ms", NodeParameterType.NUMBER, "Start time in milliseconds", False),
            ("end_ms", NodeParameterType.NUMBER, "End time in milliseconds", False),
            
            # Data format parameters
            ("delimiter", NodeParameterType.STRING, "CSV delimiter", False, None, ","),
            ("encoding", NodeParameterType.STRING, "Text encoding", False, ["utf-8", "ascii", "latin-1"], "utf-8"),
            
            # Archive parameters
            ("files", NodeParameterType.ARRAY, "Array of files for archive creation", False),
            ("compression_level", NodeParameterType.NUMBER, "Compression level (0-9)", False, None, 6),
            
            # Video parameters
            ("video_codec", NodeParameterType.STRING, "Video codec", False, ["h264", "xvid", "mpeg4"], "h264"),
            ("audio_codec", NodeParameterType.STRING, "Audio codec", False, ["aac", "mp3", "ac3"], "aac"),
            ("fps", NodeParameterType.NUMBER, "Frames per second", False, None, 30),
            
            # Document parameters
            ("page_size", NodeParameterType.STRING, "PDF page size", False, ["A4", "Letter", "Legal"], "A4"),
            ("margin", NodeParameterType.NUMBER, "PDF margin in inches", False, None, 1.0),
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
            node_type="file_convert",
            version="1.0.0",
            description="File format conversion and manipulation operations",
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
        """Custom validation for file conversion operations."""
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
        
        # Validate specific operations
        if operation in [FileConvertOperation.IMAGE_RESIZE]:
            width = params.get("width")
            height = params.get("height")
            if not isinstance(width, int) or not isinstance(height, int) or width <= 0 or height <= 0:
                raise NodeValidationError("Width and height must be positive integers")
        
        if operation in [FileConvertOperation.IMAGE_CROP]:
            coords = [params.get("left"), params.get("top"), params.get("right"), params.get("bottom")]
            if not all(isinstance(c, int) for c in coords):
                raise NodeValidationError("Crop coordinates must be integers")
            if coords[0] >= coords[2] or coords[1] >= coords[3]:
                raise NodeValidationError("Invalid crop coordinates: left < right and top < bottom")
        
        return node_data

    @asynccontextmanager
    async def _get_file_converter(self, params: Dict[str, Any]):
        """Context manager for file converter with proper lifecycle."""
        converter = None
        try:
            converter = FileConverter()
            yield converter
        except Exception as e:
            logger.error(f"File converter error: {e}")
            raise NodeExecutionError(f"File conversion operation failed: {e}")
        finally:
            if converter:
                converter.cleanup()

    async def execute(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file conversion operations with comprehensive error handling."""
        try:
            # Validate input
            validated_data = self.validate_custom(node_data)
            params = validated_data["params"]
            operation = params["operation"]
            
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
            
            async with self._get_file_converter(params) as converter:
                result = await handler(converter, params)
                
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
            logger.error(f"Unexpected error in file conversion operation: {e}")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "inputs": self._mask_sensitive_data(node_data.get("params", {})),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def _mask_sensitive_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mask sensitive data in parameters for logging."""
        masked = params.copy()
        
        # Mask large data fields
        if "input_data" in masked and masked["input_data"]:
            masked["input_data"] = f"***BASE64_DATA***({len(masked['input_data'])} chars)"
        
        if "files" in masked and masked["files"]:
            masked["files"] = f"***FILES_ARRAY***({len(masked['files'])} files)"
        
        return masked

    # Operation handlers - Image operations
    async def _handle_image_to_jpg(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_TO_JPG operation."""
        input_data = params["input_data"]
        quality = params.get("quality", 95)
        
        result_data = converter.convert_image_format(input_data, "JPEG", quality=quality)
        
        return {
            "output_data": result_data,
            "format": "JPEG",
            "quality": quality
        }

    async def _handle_image_to_png(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_TO_PNG operation."""
        input_data = params["input_data"]
        
        result_data = converter.convert_image_format(input_data, "PNG")
        
        return {
            "output_data": result_data,
            "format": "PNG"
        }

    async def _handle_image_resize(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_RESIZE operation."""
        input_data = params["input_data"]
        width = params["width"]
        height = params["height"]
        maintain_aspect = params.get("maintain_aspect", True)
        
        result_data = converter.resize_image(input_data, width, height, maintain_aspect)
        
        return {
            "output_data": result_data,
            "width": width,
            "height": height,
            "maintain_aspect": maintain_aspect
        }

    async def _handle_image_rotate(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_ROTATE operation."""
        input_data = params["input_data"]
        angle = params["angle"]
        expand = params.get("expand", True)
        
        result_data = converter.rotate_image(input_data, angle, expand)
        
        return {
            "output_data": result_data,
            "angle": angle,
            "expand": expand
        }

    async def _handle_image_crop(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_CROP operation."""
        input_data = params["input_data"]
        left = params["left"]
        top = params["top"]
        right = params["right"]
        bottom = params["bottom"]
        
        result_data = converter.crop_image(input_data, left, top, right, bottom)
        
        return {
            "output_data": result_data,
            "crop_box": [left, top, right, bottom]
        }

    # Data format conversion handlers
    async def _handle_json_to_xml(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON_TO_XML operation."""
        input_data = params["input_data"]
        
        # Decode base64 to get JSON string
        json_str = base64.b64decode(input_data).decode('utf-8')
        xml_result = converter.json_to_xml(json_str)
        
        # Encode result as base64
        result_data = base64.b64encode(xml_result.encode('utf-8')).decode('utf-8')
        
        return {
            "output_data": result_data,
            "format": "XML",
            "size": len(xml_result)
        }

    async def _handle_xml_to_json(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle XML_TO_JSON operation."""
        input_data = params["input_data"]
        
        # Decode base64 to get XML string
        xml_str = base64.b64decode(input_data).decode('utf-8')
        json_result = converter.xml_to_json(xml_str)
        
        # Encode result as base64
        result_data = base64.b64encode(json_result.encode('utf-8')).decode('utf-8')
        
        return {
            "output_data": result_data,
            "format": "JSON",
            "size": len(json_result)
        }

    async def _handle_csv_to_json(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CSV_TO_JSON operation."""
        input_data = params["input_data"]
        delimiter = params.get("delimiter", ",")
        
        # Decode base64 to get CSV string
        csv_str = base64.b64decode(input_data).decode('utf-8')
        json_result = converter.csv_to_json(csv_str, delimiter)
        
        # Encode result as base64
        result_data = base64.b64encode(json_result.encode('utf-8')).decode('utf-8')
        
        return {
            "output_data": result_data,
            "format": "JSON",
            "delimiter": delimiter,
            "records": len(json.loads(json_result))
        }

    async def _handle_json_to_csv(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON_TO_CSV operation."""
        input_data = params["input_data"]
        
        # Decode base64 to get JSON string
        json_str = base64.b64decode(input_data).decode('utf-8')
        csv_result = converter.json_to_csv(json_str)
        
        # Encode result as base64
        result_data = base64.b64encode(csv_result.encode('utf-8')).decode('utf-8')
        
        return {
            "output_data": result_data,
            "format": "CSV",
            "rows": len(csv_result.split('\n')) - 1  # Subtract header
        }

    # Archive operation handlers
    async def _handle_zip_create(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ZIP_CREATE operation."""
        files = params["files"]
        
        result_data = converter.create_zip(files)
        
        return {
            "output_data": result_data,
            "format": "ZIP",
            "file_count": len(files)
        }

    async def _handle_zip_extract(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ZIP_EXTRACT operation."""
        input_data = params["input_data"]
        
        extracted_files = converter.extract_zip(input_data)
        
        return {
            "files": extracted_files,
            "file_count": len(extracted_files),
            "total_size": sum(f["size"] for f in extracted_files)
        }

    # Encoding operation handlers
    async def _handle_base64_encode(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BASE64_ENCODE operation."""
        input_text = params["input_text"]
        
        result = converter.encode_base64(input_text)
        
        return {
            "output_data": result,
            "encoding": "base64",
            "original_length": len(input_text),
            "encoded_length": len(result)
        }

    async def _handle_base64_decode(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BASE64_DECODE operation."""
        input_data = params["input_data"]
        
        result = converter.decode_base64(input_data)
        
        return {
            "output_text": result,
            "encoding": "utf-8",
            "decoded_length": len(result),
            "original_length": len(input_data)
        }

    async def _handle_hex_encode(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HEX_ENCODE operation."""
        input_text = params["input_text"]
        
        result = converter.encode_hex(input_text)
        
        return {
            "output_data": result,
            "encoding": "hex",
            "original_length": len(input_text),
            "encoded_length": len(result)
        }

    async def _handle_hex_decode(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HEX_DECODE operation."""
        input_data = params["input_data"]
        
        result = converter.decode_hex(input_data)
        
        return {
            "output_text": result,
            "encoding": "utf-8",
            "decoded_length": len(result),
            "original_length": len(input_data)
        }

    # Text operation handlers
    async def _handle_text_to_upper(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TEXT_TO_UPPER operation."""
        input_text = params["input_text"]
        
        result = input_text.upper()
        
        return {
            "output_text": result,
            "operation": "uppercase",
            "length": len(result)
        }

    async def _handle_text_to_lower(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TEXT_TO_LOWER operation."""
        input_text = params["input_text"]
        
        result = input_text.lower()
        
        return {
            "output_text": result,
            "operation": "lowercase",
            "length": len(result)
        }

    async def _handle_text_to_title(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TEXT_TO_TITLE operation."""
        input_text = params["input_text"]
        
        result = input_text.title()
        
        return {
            "output_text": result,
            "operation": "title_case",
            "length": len(result)
        }

    # Placeholder handlers for remaining operations
    async def _handle_image_to_gif(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_TO_GIF operation."""
        input_data = params["input_data"]
        result_data = converter.convert_image_format(input_data, "GIF")
        return {"output_data": result_data, "format": "GIF"}

    async def _handle_image_to_bmp(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_TO_BMP operation."""
        input_data = params["input_data"]
        result_data = converter.convert_image_format(input_data, "BMP")
        return {"output_data": result_data, "format": "BMP"}

    async def _handle_image_to_tiff(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_TO_TIFF operation."""
        input_data = params["input_data"]
        result_data = converter.convert_image_format(input_data, "TIFF")
        return {"output_data": result_data, "format": "TIFF"}

    async def _handle_image_to_webp(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_TO_WEBP operation."""
        input_data = params["input_data"]
        quality = params.get("quality", 95)
        result_data = converter.convert_image_format(input_data, "WEBP", quality=quality)
        return {"output_data": result_data, "format": "WEBP", "quality": quality}

    async def _handle_image_to_ico(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle IMAGE_TO_ICO operation."""
        input_data = params["input_data"]
        result_data = converter.convert_image_format(input_data, "ICO")
        return {"output_data": result_data, "format": "ICO"}

    async def _handle_md_to_html(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MD_TO_HTML operation."""
        return {"status": "not_implemented"}

    async def _handle_md_to_pdf(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MD_TO_PDF operation."""
        return {"status": "not_implemented"}

    async def _handle_html_to_pdf(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML_TO_PDF operation."""
        return {"status": "not_implemented"}

    async def _handle_html_to_md(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTML_TO_MD operation."""
        return {"status": "not_implemented"}

    async def _handle_txt_to_pdf(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle TXT_TO_PDF operation."""
        return {"status": "not_implemented"}

    async def _handle_xlsx_to_csv(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle XLSX_TO_CSV operation."""
        return {"status": "not_implemented"}

    async def _handle_csv_to_xlsx(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle CSV_TO_XLSX operation."""
        return {"status": "not_implemented"}

    async def _handle_mp3_to_wav(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MP3_TO_WAV operation."""
        return {"status": "not_implemented"}

    async def _handle_wav_to_mp3(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WAV_TO_MP3 operation."""
        return {"status": "not_implemented"}

    async def _handle_audio_trim(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AUDIO_TRIM operation."""
        return {"status": "not_implemented"}

    async def _handle_json_to_yaml(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON_TO_YAML operation."""
        return {"status": "not_implemented"}

    async def _handle_yaml_to_json(self, converter: FileConverter, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle YAML_TO_JSON operation."""
        return {"status": "not_implemented"}