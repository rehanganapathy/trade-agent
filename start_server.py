#!/usr/bin/env python3
"""Start the Trade CRM server on port 5001."""
from web_app import app

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Trade CRM Server")
    print("="*60)
    print("📍 Access the application at: http://localhost:5001")
    print("="*60 + "\n")
    app.run(debug=True, port=5001, host='0.0.0.0')
