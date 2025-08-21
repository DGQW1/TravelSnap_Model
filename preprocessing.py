import os
import json
import shutil
import glob
import googlemaps
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
from pathlib import Path
from datetime import datetime
import pillow_heif
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

def create_output_directories():
    """Create the output directory structure if it doesn't exist."""
    img_dir = Path("src/processed/img")
    info_dir = Path("src/processed/info")
    img_dir.mkdir(parents=True, exist_ok=True)
    info_dir.mkdir(parents=True, exist_ok=True)
    return img_dir, info_dir

def get_gps_coordinates(exif_data):
    """Extract GPS coordinates from EXIF data."""
    gps_info = {}
    
    if 'GPSInfo' not in exif_data:
        return None
    
    gps_data = exif_data['GPSInfo']
    
    def convert_to_degrees(value):
        """Convert GPS coordinates to degrees."""
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    
    try:
        # Get latitude
        if 'GPSLatitude' in gps_data and 'GPSLatitudeRef' in gps_data:
            lat = convert_to_degrees(gps_data['GPSLatitude'])
            if gps_data['GPSLatitudeRef'] == 'S':
                lat = -lat
            gps_info['latitude'] = lat
        
        # Get longitude
        if 'GPSLongitude' in gps_data and 'GPSLongitudeRef' in gps_data:
            lon = convert_to_degrees(gps_data['GPSLongitude'])
            if gps_data['GPSLongitudeRef'] == 'W':
                lon = -lon
            gps_info['longitude'] = lon
        
        return gps_info if gps_info else None
    except (KeyError, IndexError, ValueError, TypeError):
        return None

def get_datetime_from_exif(exif_data):
    """Extract datetime from EXIF data."""
    datetime_tags = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
    
    for tag in datetime_tags:
        if tag in exif_data:
            try:
                datetime_str = exif_data[tag]
                # Parse the datetime string
                dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                return dt.isoformat()
            except (ValueError, TypeError):
                continue
    
    return None

def extract_exif_data(image_path):
    """Extract EXIF data from an image."""
    try:
        with Image.open(image_path) as img:
            exif_dict = {}
            
            # Try the modern getexif() method first (works better with HEIC)
            if hasattr(img, 'getexif'):
                exif = img.getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = value
                    
                    # Handle GPS data specifically
                    if hasattr(exif, 'get_ifd') and 0x8825 in exif:  # GPS IFD tag
                        gps_ifd = exif.get_ifd(0x8825)
                        gps_dict = {}
                        for gps_tag_id, gps_value in gps_ifd.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_dict[gps_tag] = gps_value
                        exif_dict['GPSInfo'] = gps_dict
            
            # Fallback to older method if getexif doesn't work
            elif hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif is not None:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = value
            
            return exif_dict
    except Exception as e:
        print(f"Error extracting EXIF data from {image_path}: {e}")
        return {}
    
def get_site_name(gps_coords):
    """
    Get the site name using Google Maps reverse geocoding.
    
    Args:
        gps_coords (dict): Dictionary containing 'latitude' and 'longitude' keys
    
    Returns:
        str: Site name/address or None if unavailable
    """
    if not gps_coords or 'latitude' not in gps_coords or 'longitude' not in gps_coords:
        return None
    
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    if not GOOGLE_MAPS_API_KEY:
        print("Warning: GOOGLE_MAPS_API_KEY environment variable not set. Skipping site name lookup.")
        return None
    
    try:
        gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        result = gmaps_client.reverse_geocode(
            (gps_coords['latitude'], gps_coords['longitude']), 
            language='en'
        )
        if result and len(result) > 0:
            return result[0]['formatted_address']
        return None
    except Exception as e:
        print(f"Warning: Error getting site name from Google Maps: {e}")
        return None

def convert_image_to_jpg(input_path, img_dir, info_dir, quality=95):
    """
    Convert an image to JPG format while preserving EXIF data.
    
    Args:
        input_path (Path): Path to the input image
        img_dir (Path): Output directory for images
        info_dir (Path): Output directory for JSON metadata
        quality (int): JPEG quality (1-95)
    
    Returns:
        tuple: (output_image_path, metadata_dict)
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Extract EXIF data before conversion
            exif_data = extract_exif_data(input_path)
            
            # Get GPS coordinates and datetime
            gps_coords = get_gps_coordinates(exif_data)
            datetime_taken = get_datetime_from_exif(exif_data)
            site_name = get_site_name(gps_coords)
            
            # Create metadata dictionary
            metadata = {
                "original_filename": input_path.name,
                "original_format": img.format,
                "datetime_taken": datetime_taken,
                "gps_coordinates": gps_coords,
                "image_size": img.size,
                "processing_timestamp": datetime.now().isoformat()
            }
            
            # Only add site_name if it's available
            if site_name:
                metadata["site_name"] = site_name
            
            # Convert to RGB if necessary (for PNG with transparency, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for images with transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Generate output filename
            base_name = input_path.stem
            output_image_path = img_dir / f"{base_name}.jpg"
            
            # Save as JPEG with EXIF data preserved
            exif_bytes = None
            if hasattr(img, 'getexif'):
                try:
                    exif_dict = img.getexif()
                    if exif_dict:
                        exif_bytes = exif_dict
                except:
                    pass
            
            if exif_bytes:
                img.save(output_image_path, 'JPEG', quality=quality, exif=exif_bytes)
            else:
                img.save(output_image_path, 'JPEG', quality=quality)
            
            # Save metadata as JSON
            json_path = info_dir / f"{base_name}.json"
            with open(json_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return output_image_path, metadata
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return None, None

def process_images(input_directory=".", supported_formats=None):
    """
    Process all images in the input directory.
    
    Args:
        input_directory (str): Directory containing images to process
        supported_formats (list): List of supported file extensions
    """
    if supported_formats is None:
        supported_formats = ['.jpg', '.jpeg', '.png', '.heic', '.heif']
    
    input_path = Path(input_directory)
    img_dir, info_dir = create_output_directories()
    
    if not input_path.exists():
        print(f"Input directory {input_directory} does not exist.")
        return
    
    processed_count = 0
    error_count = 0
    
    print(f"Processing images from: {input_path}")
    print(f"Images output directory: {img_dir}")
    print(f"Metadata output directory: {info_dir}")
    print("-" * 50)
    
    # Process all supported image files
    for file_path in input_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            print(f"Processing: {file_path.name}")
            
            output_path, metadata = convert_image_to_jpg(file_path, img_dir, info_dir)
            
            if output_path and metadata:
                processed_count += 1
                print(f"  ✓ Converted to: {output_path.name}")
                if metadata['gps_coordinates']:
                    print(f"  ✓ GPS: {metadata['gps_coordinates']}")
                if metadata['datetime_taken']:
                    print(f"  ✓ Date: {metadata['datetime_taken']}")
                if metadata['site_name']:
                    print(f"  ✓ Site Name: {metadata['site_name']}")
                print(f"  ✓ Metadata saved to: {file_path.stem}.json")
            else:
                error_count += 1
                print(f"  ✗ Failed to process {file_path.name}")
            
            print()
    
    print("-" * 50)
    print(f"Processing complete!")
    print(f"Successfully processed: {processed_count} images")
    print(f"Errors: {error_count} images")

def process_single_image(image_path):
    """
    Process a single image file.
    
    Args:
        image_path (str): Path to the image file
    """
    input_path = Path(image_path)
    
    if not input_path.exists():
        print(f"Image file {image_path} does not exist.")
        return
    
    if input_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.heic', '.heif']:
        print(f"Unsupported file format: {input_path.suffix}")
        return
    
    img_dir, info_dir = create_output_directories()
    output_path, metadata = convert_image_to_jpg(input_path, img_dir, info_dir)
    
    if output_path and metadata:
        print(f"Successfully processed: {input_path.name}")
        print(f"Output: {output_path}")
        print(f"Metadata: {input_path.stem}.json")
        if metadata['gps_coordinates']:
            print(f"GPS Coordinates: {metadata['gps_coordinates']}")
        if metadata['datetime_taken']:
            print(f"Date Taken: {metadata['datetime_taken']}")
    else:
        print(f"Failed to process: {input_path.name}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert images to JPG format while preserving EXIF data")
    parser.add_argument("--input", "-i", default=".", help="Input directory or single image file (default: current directory)")
    parser.add_argument("--single", "-s", action="store_true", help="Process a single image file")
    
    args = parser.parse_args()
    
    if args.single:
        process_single_image(args.input)
    else:
        process_images(args.input)
