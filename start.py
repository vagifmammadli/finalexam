"""
Production server starter
"""
from app import app, init_database
import os

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)