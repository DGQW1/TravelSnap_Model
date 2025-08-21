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

### Preprocessing

#### Process all images in the current directory:
```bash
python preprocessing.py
```

#### Process all images in a specific directory:
```bash
python preprocessing.py --input /path/to/images
```

#### Process a single image:
```bash
python preprocessing.py --single --input image.heic
```

#### Grouping Images by Location and Generating Summaries

1. **Run the grouping script:**
   ```bash
   python data_grouping/grouping.py
   ```
   This will analyze all processed images in `src/processed/img/` and their metadata in `src/processed/info/`, then group them by location and content.

2. **Output:**
   - The results are saved as `src/results/photo_groups.json`.
   - Each group contains:
     - The name of the location (if identifiable)
     - A list of photo filenames belonging to that location
     - The time range when the photos were taken
     - A brief, objective summary describing the site and the visit

      **Example Output:**

     ```json
      [
        {
          "景点名称": "斯坦福大学",
          "照片": ["IMG_6001.jpg", "IMG_6002.jpg"],
          "时间": "10:00 - 11:30",
          "总结": "美国著名大学，校园宽阔，建筑风格多样，绿化良好，适合散步和参观"
        }
      ]
      ```

4. **Use the photo viewer to preview grouped photos for testing:**
   ```bash
   python data_grouping/photo_viewer.py
   ```
   This will open a GUI to browse your grouped photos and view their metadata.

See `data_grouping/prompt.md` for more details on the grouping logic and output format.




## Output Structure

Processed files are saved to two directories:
- **Images**: `src/processed/img/` - Converted to JPG format with preserved EXIF data
- **Metadata**: `src/processed/info/` - JSON files containing extracted information

### Example JSON Output
```json
{
  "original_filename": "IMG_5634.jpeg",
  "original_format": "JPEG",
  "datetime_taken": "2025-03-21T15:55:09",
  "gps_coordinates": {
    "latitude": 36.56995277777778,
    "longitude": -121.94960833333333
  },
  "image_size": [
    3024,
    4032
  ],
  "processing_timestamp": "2025-08-20T22:58:25.054882",
  "site_name": "1700 17 Mile Dr, Pebble Beach, CA 93953, USA"
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