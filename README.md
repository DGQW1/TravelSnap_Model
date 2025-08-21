# TravelSnap Image Processing

This script automatically converts images of different formats (PNG, JPEG, HEIC) to JPG while preserving EXIF data and extracting location and timestamp information.

## Features

- **Format Conversion**: Converts PNG, JPEG, HEIC, and HEIF images to JPG format
- **EXIF Preservation**: Maintains all EXIF data during conversion
- **GPS Extraction**: Extracts longitude and latitude coordinates from EXIF data
- **Timestamp Extraction**: Retrieves the date and time when the photo was taken
- **Metadata Export**: Saves extracted information as JSON files alongside processed images
- **Batch Processing**: Can process entire directories or single images

## Installation
1. Create a conda env
```bash
conda create --name travelsnapimg python=3.11
conda activate travelSnapImg
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Process all images in the current directory:
```bash
python data_processing/preprocessing.py
```

### Process all images in a specific directory:
```bash
python data_processing/preprocessing.py --input /path/to/images
```

### Process a single image:
```bash
python data_processing/preprocessing.py --single --input image.heic
```

## Output Structure

Processed files are saved to two directories:
- **Images**: `src/processed/img/` - Converted to JPG format with preserved EXIF data
- **Metadata**: `src/processed/info/` - JSON files containing extracted information

### Example JSON Output
```json
{
  "original_filename": "IMG_1234.heic",
  "original_format": "HEIF",
  "datetime_taken": "2024-01-15T14:30:25",
  "gps_coordinates": {
    "latitude": 37.7749,
    "longitude": -122.4194
  },
  "image_size": [4032, 3024],
  "processing_timestamp": "2024-01-20T10:15:30.123456"
}
```

## Supported Formats

- **Input**: JPG, JPEG, PNG, HEIC, HEIF
- **Output**: JPG (high quality, 95% compression)

## Error Handling

The script includes comprehensive error handling for:
- Missing or corrupted EXIF data
- Unsupported file formats
- File I/O errors
- GPS coordinate parsing errors

## Notes

- Images with transparency (PNG/RGBA) are converted with a white background
- Original EXIF data is preserved whenever possible
- GPS coordinates are converted to decimal degrees
- Processing timestamp is added to track when the conversion occurred