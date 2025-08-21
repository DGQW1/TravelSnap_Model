import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def read_prompt_file():
    """Read the prompt from prompt.md file."""
    prompt_file = Path("prompt.md")
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise FileNotFoundError("prompt.md file not found in data_grouping directory")

def collect_image_metadata():
    """Collect all processed images and their metadata."""
    img_dir = Path("../src/processed/img")
    info_dir = Path("../src/processed/info")
    
    if not img_dir.exists() or not info_dir.exists():
        raise FileNotFoundError("Processed directories not found. Please run preprocessing first.")
    
    image_data = []
    
    # Get all jpg files
    for img_file in img_dir.glob("*.jpg"):
        # Find corresponding JSON file
        json_file = info_dir / f"{img_file.stem}.json"
        
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            image_data.append({
                "filename": img_file.name,
                "metadata": metadata
            })
        else:
            print(f"Warning: No metadata found for {img_file.name}")
    
    return image_data

def create_results_directory():
    """Create results directory if it doesn't exist."""
    results_dir = Path("../src/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir

def group_images_with_qwen(image_data, prompt):
    """Use Qwen to group images based on location and content."""
    try:
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        # Prepare the data for the prompt
        image_info = []
        for item in image_data:
            metadata = item["metadata"]
            info_text = f"文件名: {item['filename']}\n"
            
            if metadata.get('datetime_taken'):
                info_text += f"拍摄时间: {metadata['datetime_taken']}\n"
            
            if metadata.get('gps_coordinates'):
                coords = metadata['gps_coordinates']
                info_text += f"GPS坐标: 纬度{coords['latitude']:.6f}, 经度{coords['longitude']:.6f}\n"
            
            if metadata.get('original_format'):
                info_text += f"原始格式: {metadata['original_format']}\n"
            
            image_info.append(info_text)
        
        # Combine prompt with image data
        full_prompt = f"{prompt}\n\n以下是照片信息：\n\n" + "\n---\n".join(image_info)
        
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "你是一个专业的旅行照片分析师，擅长根据照片的GPS坐标、拍摄时间和内容来识别和分组旅行地点。"},
                {"role": "user", "content": full_prompt},
            ],
            temperature=0.1,  # Lower temperature for more consistent results
        )
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"错误信息：{e}")
        print("请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
        return None

def save_grouping_results(results, results_dir):
    """Save the grouping results to a JSON file."""
    output_file = results_dir / "photo_groups.json"
    
    try:
        # Try to parse the result as JSON to validate it
        if isinstance(results, str):
            # If results is a string, try to extract JSON from it
            import re
            json_match = re.search(r'\[.*\]', results, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_results = json.loads(json_str)
            else:
                # If no JSON found, save as raw text
                with open(results_dir / "photo_groups_raw.txt", 'w', encoding='utf-8') as f:
                    f.write(results)
                print(f"Results saved as raw text to: {results_dir / 'photo_groups_raw.txt'}")
                return
        else:
            parsed_results = results
        
        # Save as formatted JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_results, f, ensure_ascii=False, indent=2)
        
        print(f"Grouping results saved to: {output_file}")
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, save as raw text
        with open(results_dir / "photo_groups_raw.txt", 'w', encoding='utf-8') as f:
            f.write(str(results))
        print(f"Could not parse as JSON, saved raw results to: {results_dir / 'photo_groups_raw.txt'}")
        print(f"JSON Error: {e}")

def main():
    """Main function to process images and group them."""
    try:
        print("Reading prompt...")
        prompt = read_prompt_file()
        
        print("Collecting image metadata...")
        image_data = collect_image_metadata()
        print(f"Found {len(image_data)} images with metadata")
        
        if not image_data:
            print("No images found to process!")
            return
        
        print("Grouping images with Qwen...")
        results = group_images_with_qwen(image_data, prompt)
        
        if results:
            print("Saving results...")
            results_dir = create_results_directory()
            save_grouping_results(results, results_dir)
            print("Processing complete!")
        else:
            print("Failed to get results from Qwen")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()