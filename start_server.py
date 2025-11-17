#!/usr/bin/env python3
"""Start the Trade CRM server on port 5000."""
from crm_app import app, db

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Trade CRM Server")
    print("="*60)
    print("📍 Access the application at: http://localhost:5000")
    print("="*60 + "\n")

    # Initialize database
    with app.app_context():
        db.create_all()

    app.run(debug=True, port=5000, host='0.0.0.0')
