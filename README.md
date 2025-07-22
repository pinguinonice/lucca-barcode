# Lucca Barcode Generator

A web-based barcode generation application built with Flask. This application allows users to generate and customize barcodes, which can be downloaded or integrated into PDF documents.

## Features

- Generate various types of barcodes
- Upload and process PDF files
- Customize barcode appearance and placement
- Download generated barcodes
- Web-based interface for easy access
- Session management for temporary storage

## Prerequisites

Before you begin, ensure you have installed:
- Docker and Docker Compose
- Git (for cloning the repository)

For local development without Docker, you'll need:
- Python 3.11 or higher
- poppler-utils (for PDF processing)
- pip (Python package manager)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/lucca-barcode.git
   cd lucca-barcode
   ```

2. Run the application using the provided script:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

   The application will be available at `http://localhost:5099`

### Manual Installation (Development)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/lucca-barcode.git
   cd lucca-barcode
   ```

2. Install poppler-utils:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install poppler-utils
     ```
   - On macOS:
     ```bash
     brew install poppler
     ```
   - On Windows:
     Download and install from: http://blog.alivate.com.au/poppler-windows/

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   cd website
   python run.py
   ```

   The application will be available at `http://localhost:5099`

## Project Structure

```
lucca-barcode/
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── run.sh                 # Startup script
└── website/
    ├── run.py            # Application entry point
    └── app/
        ├── __init__.py   # Flask app initialization
        ├── config.py     # Configuration settings
        ├── routes.py     # URL routes and views
        ├── pdf_utils.py  # PDF processing utilities
        ├── static/       # Static files (CSS, uploads)
        └── templates/    # HTML templates
```

## Configuration

The application can be configured using environment variables:

- `FLASK_ENV`: Set to 'production' or 'development'
- `FLASK_DEBUG`: Enable/disable debug mode (true/false)
- `FLASK_HOST`: Host to bind to (default: 0.0.0.0)
- `FLASK_PORT`: Port to run on (default: 5099)
- `SECRET_KEY`: Flask secret key for session management

These can be set in the `docker-compose.yml` file or in your environment.

## Usage

1. Access the web interface at `http://localhost:5099`
2. Upload a PDF file or generate a new barcode
3. Customize the barcode settings as needed
4. Download the generated barcode or modified PDF

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Troubleshooting

Common issues and solutions:

1. **ERR_EMPTY_RESPONSE**: 
   - Ensure Docker is running
   - Check if port 5099 is available
   - Verify all dependencies are installed

2. **PDF Processing Issues**:
   - Confirm poppler-utils is properly installed
   - Check file permissions in uploads directory
   - Verify PDF file is not corrupted

3. **Docker Issues**:
   - Run `docker-compose down` and then `docker-compose up --build`
   - Check Docker logs: `docker-compose logs`
   - Verify Docker daemon is running

## License

[Your License Here]

## Contact

[Your Contact Information] 