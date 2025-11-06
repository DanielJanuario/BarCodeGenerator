import pandas as pd
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import math
import io
import os

def get_available_barcode_formats():
    """Check available barcode formats"""
    print("Available barcode formats:")
    print(barcode.PROVIDED_BARCODES)

def create_barcode_image(number, barcode_text, width_mm=34, height_mm=23):
    """Create a single barcode label with number above the barcode"""
    # Convert mm to pixels (assuming 300 DPI)
    mm_to_px = 300 / 25.4
    width_px = int(width_mm * mm_to_px)
    height_px = int(height_mm * mm_to_px)
    
    # Create label canvas
    label = Image.new('RGB', (width_px, height_px), 'white')
    draw = ImageDraw.Draw(label)
    
    # Try different barcode formats
    barcode_success = False
    
    # Try Code 128 first (most reliable)
    try:
        code128 = barcode.get_barcode_class('code128')
        writer_options = {
            'write_text': False,
            'module_height': 8.0,
            'module_width': .5,      # Thicker bars
            'quiet_zone': 1.0,
            'dpi': 600
        }
        
        barcode_obj = code128(barcode_text, writer=ImageWriter())
        barcode_img = barcode_obj.render(writer_options=writer_options)
        barcode_success = True
        print(f"Successfully generated Code128 barcode for: {barcode_text}")
        
    except Exception as e:
        print(f"Code128 failed for {barcode_text}: {e}")
    
    if barcode_success:
        # REDUCED SIZE: Add margins by using smaller percentage of available space
        barcode_width = int(width_px * 0.85)  # 85% of label width (7.5% margin on each side)
        barcode_height = int(height_px * 0.5)  # 50% of label height (reduced to make space for text below)
        barcode_img = barcode_img.resize((barcode_width, barcode_height), Image.Resampling.LANCZOS)
        
        # Center the barcode with margins
        barcode_x = (width_px - barcode_width) // 2
        barcode_y = int(height_px * 0.25)  # Moved up to make space for text below
        label.paste(barcode_img, (barcode_x, barcode_y))
    else:
        # Draw error placeholder
        print(f"All barcode formats failed for: {barcode_text}")
        draw.rectangle([width_px//4, height_px//3, 3*width_px//4, 2*height_px//3], 
                      outline='red', width=2)
        draw.text((width_px//2-40, height_px//2-10), "BARCODE ERROR", fill='red')
        # Also show the barcode text that failed
        draw.text((width_px//2-60, height_px//2+10), barcode_text, fill='red')
    
    # Add number text above barcode - smaller size
    try:
        font_size = int(height_px * 0.12)  # REDUCED font size
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
    
    if font:
        text_bbox = draw.textbbox((0, 0), str(number), font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width_px - text_width) // 2
        text_y = int(height_px * 0.08)  # Higher up for the number
        draw.text((text_x, text_y), str(number), fill='black', font=font)
    
    # ADD BARCODE TEXT BELOW THE BARCODE
    try:
        # Use smaller font for barcode text
        barcode_font_size = int(height_px * 0.09)  # Even smaller font for barcode text
        barcode_font = ImageFont.truetype("arial.ttf", barcode_font_size)
    except:
        try:
            barcode_font = ImageFont.truetype("Arial.ttf", barcode_font_size)
        except:
            try:
                barcode_font = ImageFont.load_default()
            except:
                barcode_font = None
    
    if barcode_font:
        barcode_text_bbox = draw.textbbox((0, 0), barcode_text, font=barcode_font)
        barcode_text_width = barcode_text_bbox[2] - barcode_text_bbox[0]
        barcode_text_x = (width_px - barcode_text_width) // 2
        barcode_text_y = int(height_px * 0.78)  # Position below the barcode
        draw.text((barcode_text_x, barcode_text_y), barcode_text, fill='black', font=barcode_font)
    
    # Optional: Draw a border around the label to visualize margins
    # Uncomment the line below if you want to see the label boundaries
    # draw.rectangle([1, 1, width_px-2, height_px-2], outline='lightgray', width=1)
    
    return label

def generate_row_images(csv_file, output_dir='row_images'):
    """Generate separate rotated images for each row of barcode labels"""
    # First, check available barcode formats
    get_available_barcode_formats()
    
    # Read CSV file
    df = pd.read_csv(csv_file, header=None, names=['number', 'barcode'])
    
    # Print the barcode texts to verify
    print("\nBarcode texts from CSV:")
    for i, row in df.iterrows():
        print(f"  Row {i}: '{row['barcode']}' (length: {len(row['barcode'])})")
    
    # Constants in mm
    SHEET_WIDTH_MM = 102
    LABEL_WIDTH_MM = 34
    LABEL_HEIGHT_MM = 23
    HORIZONTAL_GAP_MM = 0
    VERTICAL_GAP_MM = 4
    COLS = 3
    
    # Convert mm to pixels (300 DPI)
    mm_to_px = 300 / 25.4
    sheet_width_px = int(SHEET_WIDTH_MM * mm_to_px)
    label_width_px = int(LABEL_WIDTH_MM * mm_to_px)
    label_height_px = int(LABEL_HEIGHT_MM * mm_to_px)
    vertical_gap_px = int(VERTICAL_GAP_MM * mm_to_px)
    
    # Calculate rows needed
    total_labels = len(df)
    rows = math.ceil(total_labels / COLS)
    
    # Create output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate each row as a separate image
    for row_num in range(rows):
        # Calculate row height (same as before)
        row_height_px = label_height_px
        
        # Create row image (will be rotated later)
        row_image = Image.new('RGB', (sheet_width_px, row_height_px), 'white')
        
        # Calculate label positions
        horizontal_gap_px = (sheet_width_px - (COLS * label_width_px)) // (COLS + 1)
        
        # Add labels to this row
        for col in range(COLS):
            index = row_num * COLS + col
            if index < total_labels:
                # Get the barcode text
                barcode_text = df.iloc[index]['barcode']
                print(f"\nProcessing barcode {index}: '{barcode_text}'")
                
                # Create individual label
                label_img = create_barcode_image(
                    df.iloc[index]['number'], 
                    barcode_text, 
                    LABEL_WIDTH_MM, 
                    LABEL_HEIGHT_MM
                )
                
                # Calculate position
                x = horizontal_gap_px + col * (label_width_px + horizontal_gap_px)
                y = 0
                
                # Paste label onto row image
                row_image.paste(label_img, (x, y))
        
        # Rotate the row image 90 degrees clockwise
        rotated_image = row_image.rotate(-90, expand=True)
        
        # Save the rotated row image
        output_file = os.path.join(output_dir, f'row_{row_num + 1}.png')
        rotated_image.save(output_file, 'PNG', dpi=(300, 300))
        
        print(f"\nGenerated: {output_file}")
        print(f"Original dimensions: {sheet_width_px/mm_to_px:.1f}mm x {row_height_px/mm_to_px:.1f}mm")
        print(f"Rotated dimensions: {rotated_image.width/mm_to_px:.1f}mm x {rotated_image.height/mm_to_px:.1f}mm")
        print(f"Labels in this row: {min(COLS, total_labels - row_num * COLS)}")
        print("-" * 50)
    
    print(f"All row images generated in '{output_dir}' directory")
    print(f"Total rows: {rows}")

# Example usage
if __name__ == "__main__":
    # Generate the row images
    generate_row_images('sample_codes.csv', 'row_images')