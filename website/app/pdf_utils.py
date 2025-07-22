import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter, landscape
from reportlab.lib.units import mm
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os

def generate_barcode_image(number, branding_text="", logo_path=None, logo_size=100, text_size=100):
    """Generate a single barcode image with branding matching the example layout"""
    # Generate barcode with wider bars
    code39 = barcode.get_barcode_class('code39')
    
    # Configure ImageWriter for wider barcode
    writer = ImageWriter()
    writer.set_options({
        'module_width': 0.4,  # Make bars wider (default is 0.2)
        'module_height': 15,  # Taller bars
        'quiet_zone': 6.5,    # Space around barcode
        'font_size': 0,       # No text under barcode (we'll add our own)
        'text_distance': 0,   # No distance for text
        'write_text': False,  # Explicitly disable text rendering
        'background': 'white',
        'foreground': 'black'
    })
    
    barcode_obj = code39(str(number), writer=writer, add_checksum=False)
    
    # Save barcode to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        barcode_path = tmp.name
    barcode_obj.save(barcode_path[:-4])  # remove .png as barcode library adds it
    barcode_path = barcode_path[:-4] + '.png'
    
    # Load barcode image
    barcode_img = Image.open(barcode_path)
    
    # Layout dimensions (matching the example)
    header_height = 80  # Space for logo + branding text side by side
    number_height = 30  # Space for number below barcode
    padding = 10
    
    # Scale up the barcode for even more width if needed
    barcode_scale = 1.2  # Make barcode 20% larger
    scaled_barcode_width = int(barcode_img.width * barcode_scale)
    scaled_barcode_height = int(barcode_img.height * barcode_scale)
    barcode_img = barcode_img.resize((scaled_barcode_width, scaled_barcode_height), Image.Resampling.LANCZOS)
    
    # Calculate final image size
    img_width = max(barcode_img.width, 300)  # Minimum width for header layout
    img_height = header_height + barcode_img.height + number_height + (padding * 2)
    
    # Create final image with white background
    final_img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(final_img)
    
    y_offset = padding
    
    # Header section: Logo on left, Branding text on right
    if logo_path and os.path.exists(logo_path) or branding_text:
        header_y = y_offset
        
        # Add logo on the left
        logo_width = 0
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                # Make logo square and resize to fit header with size adjustment
                base_logo_size = header_height - 20  # Base size
                adjusted_logo_size = int(base_logo_size * logo_size / 100)  # Apply size percentage
                logo.thumbnail((adjusted_logo_size, adjusted_logo_size), Image.Resampling.LANCZOS)
                
                # Center logo vertically in header
                logo_y = header_y + (header_height - logo.height) // 2
                final_img.paste(logo, (padding, logo_y))
                logo_width = logo.width + padding
            except Exception:
                pass
        
        # Add branding text on the right
        if branding_text:
            try:
                # Use larger font for branding with size adjustment
                base_font_size = 18
                adjusted_font_size = int(base_font_size * text_size / 100)  # Apply size percentage
                font = ImageFont.truetype("Arial.ttf", adjusted_font_size)
            except:
                font = ImageFont.load_default()
            
            # Position text to the right of logo
            text_x = logo_width + padding * 2
            
            # Center text vertically in header
            bbox = draw.textbbox((0, 0), branding_text, font=font)
            text_height = bbox[3] - bbox[1]
            text_y = header_y + (header_height - text_height) // 2
            
            draw.text((text_x, text_y), branding_text, fill='black', font=font)
        
        y_offset += header_height
    
    # Add barcode (centered horizontally)
    barcode_x = (img_width - barcode_img.width) // 2
    final_img.paste(barcode_img, (barcode_x, y_offset))
    y_offset += barcode_img.height + padding
    
    # Add number below barcode (centered)
    try:
        number_font = ImageFont.truetype("Arial.ttf", 16)
    except:
        number_font = ImageFont.load_default()
    
    number_text = str(number)
    bbox = draw.textbbox((0, 0), number_text, font=number_font)
    number_width = bbox[2] - bbox[0]
    number_x = (img_width - number_width) // 2
    
    draw.text((number_x, y_offset), number_text, fill='black', font=number_font)
    
    # Clean up temporary barcode file
    os.unlink(barcode_path)
    
    return final_img

def generate_barcodes_pdf(settings, output_path):
    """Generate PDF with barcodes based on settings"""
    start_num = settings.get('start_number', 1)
    count = settings.get('count', 1)
    layout = settings.get('layout', 'single')
    branding = settings.get('branding', '')
    logo_path = settings.get('logo_path')
    
    # Set page orientation based on layout
    if layout == 'single':
        # Single layout uses landscape orientation
        c = canvas.Canvas(output_path, pagesize=landscape(A4))
        page_width, page_height = landscape(A4)
    else:
        # Grid layout uses portrait orientation  
        c = canvas.Canvas(output_path, pagesize=A4)
        page_width, page_height = A4
    
    if layout == 'single':
        # One barcode per page (A4 landscape)
        for i in range(count):
            number = start_num + i
            
            # Generate barcode image
            logo_size = settings.get('logo_size', 100)
            text_size = settings.get('text_size', 100)
            barcode_img = generate_barcode_image(number, branding, logo_path, logo_size, text_size)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                img_path = tmp.name
            barcode_img.save(img_path)
            
            # Add to PDF (centered on A4 landscape page)
            img_width = barcode_img.width
            img_height = barcode_img.height
            
            # Scale to fit page (max 80% of page width, 60% of page height for better proportions)
            max_width = page_width * 0.8
            max_height = page_height * 0.6
            
            # Apply user's size adjustment for single page layout
            single_size = settings.get('single_size', 100)
            size_multiplier = single_size / 100.0
            
            scale = min(max_width / img_width, max_height / img_height) * size_multiplier
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            
            # Center on A4 landscape page
            x = (page_width - scaled_width) / 2
            y = (page_height - scaled_height) / 2
            
            c.drawImage(img_path, x, y, scaled_width, scaled_height)
            c.showPage()
            
            # Clean up
            os.unlink(img_path)
    
    else:
        # Grid layout for sticker sheets (A4 portrait)
        rows = settings.get('rows', 8)
        cols = settings.get('cols', 3)
        x_spacing = settings.get('x_spacing', 0) * mm
        y_spacing = settings.get('y_spacing', 0) * mm
        left_offset = settings.get('left_offset', 0) * mm
        top_offset = settings.get('top_offset', 0) * mm
        
        codes_per_page = rows * cols
        total_pages = (count + codes_per_page - 1) // codes_per_page
        
        # Calculate sticker dimensions based on A4 and grid
        base_margin = 10 * mm  # Base margin from edges
        available_width = page_width - 2 * base_margin - (cols - 1) * x_spacing
        available_height = page_height - 2 * base_margin - (rows - 1) * y_spacing
        sticker_width = available_width / cols
        sticker_height = available_height / rows
        
        for page in range(total_pages):
            codes_on_this_page = min(codes_per_page, count - page * codes_per_page)
            
            for i in range(codes_on_this_page):
                row = i // cols
                col = i % cols
                number = start_num + page * codes_per_page + i
                
                # Generate barcode image
                logo_size = settings.get('logo_size', 100)
                text_size = settings.get('text_size', 100)
                barcode_img = generate_barcode_image(number, branding, logo_path, logo_size, text_size)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    img_path = tmp.name
                barcode_img.save(img_path)
                
                # Calculate sticker position with offsets
                x = base_margin + left_offset + col * (sticker_width + x_spacing)
                y = page_height - base_margin - top_offset - (row + 1) * sticker_height - row * y_spacing
                
                # Scale barcode to fit sticker with some padding
                padding = 2 * mm
                max_barcode_width = sticker_width - 2 * padding
                max_barcode_height = sticker_height - 2 * padding
                
                scale = min(max_barcode_width / barcode_img.width, max_barcode_height / barcode_img.height)
                scaled_width = barcode_img.width * scale
                scaled_height = barcode_img.height * scale
                
                # Center barcode in sticker
                barcode_x = x + (sticker_width - scaled_width) / 2
                barcode_y = y + (sticker_height - scaled_height) / 2
                
                c.drawImage(img_path, barcode_x, barcode_y, scaled_width, scaled_height)
                
                # Clean up
                os.unlink(img_path)
            
            c.showPage()
    
    c.save()

def generate_preview_pdf(settings):
    """Generate a preview PDF showing the actual first page"""
    # Create a temporary PDF with just the first page
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        preview_pdf_path = tmp.name
    
    # Generate the actual PDF (but limit to first page for preview)
    original_count = settings.get('count', 1)
    layout = settings.get('layout', 'single')
    
    if layout == 'single':
        # For single layout, show just one barcode (landscape)
        preview_settings = settings.copy()
        preview_settings['count'] = 1
    else:
        # For grid layout, show first page worth of barcodes (portrait)
        rows = settings.get('rows', 8)
        cols = settings.get('cols', 3)
        codes_per_page = rows * cols
        preview_settings = settings.copy()
        preview_settings['count'] = min(original_count, codes_per_page)
    
    # Generate the preview PDF
    generate_barcodes_pdf(preview_settings, preview_pdf_path)
    
    return preview_pdf_path

def convert_pdf_to_image(pdf_path):
    """Convert first page of PDF to PNG image for web display"""
    try:
        # Try to use pdf2image if available
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
        
        if images:
            # Save as PNG
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                png_path = tmp.name
            images[0].save(png_path, 'PNG')
            return png_path
    except ImportError:
        pass
    
    # Fallback: Use reportlab to render PDF to image
    try:
        from reportlab.graphics import renderPM
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib.pagesizes import A4
        
        # Create a simple image showing "PDF Preview"
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            png_path = tmp.name
        
        # Create a basic preview image
        img = Image.new('RGB', (595, 842), 'white')  # A4 dimensions in pixels
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((297, 421), "PDF Preview Generated", fill='black', anchor='mm', font=font)
        draw.text((297, 450), f"Open PDF to see actual content", fill='gray', anchor='mm')
        
        img.save(png_path)
        return png_path
        
    except Exception:
        # Ultimate fallback
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            png_path = tmp.name
        
        img = Image.new('RGB', (400, 200), 'white')
        draw = ImageDraw.Draw(img)
        draw.text((200, 100), 'Preview unavailable', fill='red', anchor='mm')
        img.save(png_path)
        return png_path

def generate_preview_image(settings):
    """Generate a preview image by creating actual PDF and converting first page"""
    # Generate the actual PDF preview
    pdf_path = generate_preview_pdf(settings)
    
    # Convert PDF to image
    png_path = convert_pdf_to_image(pdf_path)
    
    # Clean up temporary PDF
    os.unlink(pdf_path)
    
    return png_path 