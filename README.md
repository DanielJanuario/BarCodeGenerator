# Barcode Label Generator

A Python script that generates rotated barcode labels from CSV data. Creates individual images for each row with Code 128 barcodes, numbers, and barcode text.

## Features
- Reads barcode data from CSV files
- Generates individual labels with:
  - Number at the top
  - Code 128 barcode in the middle
  - Barcode text below
- Automatically rotates labels 90 degrees
- Precise dimensions (34 mm × 23 mm per label)
- 300 DPI resolution for print quality
- Creates separate image files for each row

## Requirements
- Python 3.6+
- Required packages:
```bash
pip install pandas python-barcode pillow
```

## CSV Format
Create a CSV file with the following format:
```
number,barcode_text
```
Example:
```
1,0123456789AB
2,0123456789CD
1,0123456789EF
14,0123456789GH
```
- First column: Number to display above barcode
- Second column: Barcode text (12 characters recommended)

## Usage
Prepare your CSV file (e.g., `sample_codes.csv`) and run:
```bash
python barcode_generator.py
```
Output:
- Creates `row_images/` directory
- Generates `row_1.png`, `row_2.png`, etc.
- Each file contains 3 labels rotated 90 degrees

## Label Specifications
- Label size: 34 mm × 23 mm
- Sheet width: 102 mm (fits 3 labels per row)
- Vertical gap: 4 mm between rows
- Resolution: 300 DPI
- Barcode format: Code 128
- Rotation: 90 degrees clockwise

## File Structure
```
project/
├── barcode_generator.py    # Main script
├── sample_codes.csv        # Input CSV file
└── row_images/             # Output directory
    ├── row_1.png
    ├── row_2.png
    └── ...
```

## Customization

### Adjust Label Dimensions
Modify these constants in `generate_row_images()`:
```python
SHEET_WIDTH_MM = 102
LABEL_WIDTH_MM = 34
LABEL_HEIGHT_MM = 23
VERTICAL_GAP_MM = 4
COLS = 3
```

### Adjust Barcode Appearance
Modify `writer_options` in `create_barcode_image()`:
```python
writer_options = {
    'write_text': False,
    'module_height': 8.0,    # Bar height
    'module_width': 0.5,     # Bar thickness
    'quiet_zone': 1.0,       # White space around barcode
    'dpi': 600,              # Resolution
}
```

### Adjust Text Sizes and Positions
Modify these values in `create_barcode_image()`:
```python
# Number text
font_size = int(height_px * 0.12)
text_y = int(height_px * 0.08)

# Barcode text
barcode_font_size = int(height_px * 0.09)
barcode_text_y = int(height_px * 0.78)
```

## Output Example
Each generated PNG file will contain 3 labels arranged vertically (after rotation):

```
┌──────────────┐
│      1       │  ← Number
│   ████████   │  ← Barcode
│  0123456789AB│  ← Barcode text
├──────────────┤
│      2       │
│   ████████   │
│  0123456789CD│
├──────────────┤
│      1       │
│   ████████   │
│  0123456789EF│
└──────────────┘
```

## Troubleshooting

### Barcode Generation Errors
- Ensure barcode text contains only valid characters for Code 128
- Check that the CSV file is properly formatted
- Verify all required packages are installed

### Image Quality Issues
- The script uses 300 DPI for high-quality printing
- Adjust `dpi` in `writer_options` for higher/lower resolution

### File Not Found
- Ensure CSV file is in the same directory as the script
- Check that the CSV filename matches in the main function call

## License
This script is provided as-is for generating barcode labels.