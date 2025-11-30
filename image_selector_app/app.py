import os
from flask import Flask, render_template, request, redirect, url_for, session
from PIL import Image # Import Pillow for dimensions

app = Flask(__name__)
app.secret_key = 'a_very_secret_key_change_this_in_production'

# --- Configuration ---
# CHANGE THIS TO YOUR IMAGE DIRECTORY!
IMAGE_DIR = 'image_selector_app/static/images/'
PAGE_SIZES = [10, 50, 100, 0] # 0 for "All"

# --- Helper Functions ---

def format_file_size(size_bytes):
    """Converts bytes to a human-readable format (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    size_bytes /= 1024
    if size_bytes < 1024:
        return f"{size_bytes:.1f} KB"
    size_bytes /= 1024
    return f"{size_bytes:.1f} MB"

def get_image_metadata(filename):
    """Gathers filename, size, and dimensions."""
    full_path = os.path.join(IMAGE_DIR, filename)
    metadata = {
        'filename': filename,
        'size': 'N/A',
        'dimensions': 'N/A',
        'is_valid': True # Flag for valid image
    }
    
    try:
        # Get file size
        metadata['size'] = format_file_size(os.path.getsize(full_path))
        
        # Get image dimensions using Pillow
        with Image.open(full_path) as img:
            metadata['dimensions'] = f"{img.width}x{img.height}"
            
    except FileNotFoundError:
        metadata['size'] = 'File Not Found'
        metadata['is_valid'] = False
    except Exception:
        # Catches PIL errors (not a valid image format)
        metadata['dimensions'] = 'Error'
        
    return metadata

def get_image_list():
    """Reads all image files from the directory."""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    try:
        all_files = sorted(os.listdir(IMAGE_DIR))
        all_images = [
            f for f in all_files
            if f.lower().endswith(valid_extensions)
        ]
        return all_images
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# --- Routes ---

# ... (before_request and results routes remain the same) ...

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:page_num>', methods=['GET', 'POST'])
def index(page_num=1):
    all_image_filenames = get_image_list()
    
    if request.method == 'POST':
        # ... (POST request logic remains the same, except for using request.form.getlist('selected_filenames')) ...
        selected_images = request.form.getlist('selected_filenames') # Note the changed input name
        command_template = request.form.get('command_template', 'echo {}')

        # ... (Script generation logic remains the same) ...
        # (Omitted for brevity, but it must be included)
        
        # ... (Redirect to results) ...

    # Handle GET request (Displaying the Image Selector)
    page_size_str = request.args.get('page_size', str(PAGE_SIZES[0]))
    try:
        page_size = int(page_size_str)
        if page_size not in PAGE_SIZES:
            page_size = PAGE_SIZES[0]
    except ValueError:
        page_size = PAGE_SIZES[0]
    
    # Pagination Logic
    # ... (Pagination logic remains the same) ...
    if page_size == 0: 
        images_to_process = all_image_filenames
        total_pages = 1
        page_num = 1
    else:
        total_images = len(all_image_filenames)
        total_pages = (total_images + page_size - 1) // page_size
        
        if page_num < 1: page_num = 1
        if page_num > total_pages and total_pages > 0: page_num = total_pages
        
        start_index = (page_num - 1) * page_size
        end_index = start_index + page_size
        images_to_process = all_image_filenames[start_index:end_index]

    # --- New: Get metadata for displayed images ---
    images_with_metadata = [get_image_metadata(f) for f in images_to_process]
    
    # Pass data to the template
    return render_template('index.html', 
                           images=images_with_metadata, # Pass the list with metadata
                           page_num=page_num, 
                           total_pages=total_pages, 
                           page_size=page_size,
                           page_sizes=PAGE_SIZES,
                           total_image_count=len(all_image_filenames),
                           template_command=request.form.get('command_template', 'convert {} -resize 50% {n}_thumb.jpg') 
                           )


if __name__ == '__main__':
    app.run(debug=True)
