from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, jsonify
import os
import tempfile
import time
from .pdf_utils import generate_barcodes_pdf, generate_preview_image

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    # Load previous settings from session
    settings = session.get('barcode_settings', {
        'start_number': 1,
        'count': 10,
        'layout': 'single',
        'rows': 2,
        'cols': 3,
        'spacing': 5,
        'branding': ''
    })
    
    if request.method == 'POST':
        # Update settings from form
        settings.update({
            'start_number': int(request.form.get('start_number', 1)),
            'count': int(request.form.get('count', 10)),
            'layout': request.form.get('layout', 'single'),
            'rows': int(request.form.get('rows', 8)) if request.form.get('rows') else 8,
            'cols': int(request.form.get('cols', 3)) if request.form.get('cols') else 3,
            'x_spacing': float(request.form.get('x_spacing', 0)) if request.form.get('x_spacing') else 0,
            'y_spacing': float(request.form.get('y_spacing', 0)) if request.form.get('y_spacing') else 0,
            'left_offset': float(request.form.get('left_offset', 0)) if request.form.get('left_offset') else 0,
            'top_offset': float(request.form.get('top_offset', 0)) if request.form.get('top_offset') else 0,
            'logo_size': int(request.form.get('logo_size', 100)) if request.form.get('logo_size') else 100,
            'text_size': int(request.form.get('text_size', 100)) if request.form.get('text_size') else 100,
            'single_size': int(request.form.get('single_size', 100)) if request.form.get('single_size') else 100,
            'branding': request.form.get('branding', '')
        })
        
        # Handle logo upload
        logo_path = None
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo.filename:
                logo_path = os.path.join('app/static/uploads', logo.filename)
                os.makedirs(os.path.dirname(logo_path), exist_ok=True)
                logo.save(logo_path)
                settings['logo_path'] = logo_path
        
        # Save settings to session
        session['barcode_settings'] = settings
        
        # Suggest next start number for next batch
        next_start = settings['start_number'] + settings['count']
        session['next_start_suggestion'] = next_start
        
        # Generate preview after form submission
        try:
            preview_path = generate_preview_image(settings)
            # Copy preview to static folder so it can be served
            static_preview_path = 'app/static/preview.png'
            os.makedirs(os.path.dirname(static_preview_path), exist_ok=True)
            import shutil
            shutil.copy(preview_path, static_preview_path)
            os.unlink(preview_path)  # Clean up temp file
            settings['has_preview'] = True
            settings['timestamp'] = str(int(time.time()))  # Add timestamp for cache busting
        except Exception as e:
            settings['preview_error'] = str(e)
            settings['has_preview'] = False
    
    # Get next start suggestion
    settings['next_start_suggestion'] = session.get('next_start_suggestion', settings['start_number'])
    
    return render_template('index.html', settings=settings)

@main.route('/preview')
def preview():
    settings = session.get('barcode_settings', {})
    if not settings:
        return jsonify({'error': 'No settings found'}), 400
    
    try:
        preview_path = generate_preview_image(settings)
        return send_file(preview_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/generate', methods=['POST'])
def generate():
    # Process form data first, just like in the index route
    settings = session.get('barcode_settings', {
        'start_number': 1,
        'count': 10,
        'layout': 'single',
        'rows': 8,
        'cols': 3,
        'x_spacing': 0,
        'y_spacing': 0,
        'left_offset': 0,
        'top_offset': 0,
        'logo_size': 100,
        'text_size': 100,
        'single_size': 100,
        'branding': ''
    })
    
    # Update settings from current form data
    settings.update({
        'start_number': int(request.form.get('start_number', 1)),
        'count': int(request.form.get('count', 10)),
        'layout': request.form.get('layout', 'single'),
        'rows': int(request.form.get('rows', 8)) if request.form.get('rows') else 8,
        'cols': int(request.form.get('cols', 3)) if request.form.get('cols') else 3,
        'x_spacing': float(request.form.get('x_spacing', 0)) if request.form.get('x_spacing') else 0,
        'y_spacing': float(request.form.get('y_spacing', 0)) if request.form.get('y_spacing') else 0,
        'left_offset': float(request.form.get('left_offset', 0)) if request.form.get('left_offset') else 0,
        'top_offset': float(request.form.get('top_offset', 0)) if request.form.get('top_offset') else 0,
        'logo_size': int(request.form.get('logo_size', 100)) if request.form.get('logo_size') else 100,
        'text_size': int(request.form.get('text_size', 100)) if request.form.get('text_size') else 100,
        'single_size': int(request.form.get('single_size', 100)) if request.form.get('single_size') else 100,
        'branding': request.form.get('branding', '')
    })
    
    # Handle logo upload
    if 'logo' in request.files:
        logo = request.files['logo']
        if logo.filename:
            logo_path = os.path.join('app/static/uploads', logo.filename)
            os.makedirs(os.path.dirname(logo_path), exist_ok=True)
            logo.save(logo_path)
            settings['logo_path'] = logo_path
    
    # Save updated settings to session
    session['barcode_settings'] = settings
    
    try:
        # Generate PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf_path = tmp.name
        
        generate_barcodes_pdf(settings, pdf_path)
        
        return send_file(
            pdf_path, 
            as_attachment=True, 
            download_name=f'barcodes_{settings.get("start_number", 1)}-{settings.get("start_number", 1) + settings.get("count", 1) - 1}.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return f'Error generating PDF: {str(e)}', 500 