from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get host from environment or default to 0.0.0.0 for Docker
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5099))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug) 