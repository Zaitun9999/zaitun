# main.py - Hosted permanently on Render
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)  # Allows your GitHub Pages form to talk to this server

# Render automatically provides your database string if you configure it as an environment variable
DB_URI = os.getenv("DATABASE_URL")

@app.route('/api/submit', methods=['POST'])
def handle_submission():
    data = request.json
    full_name = data.get('fullName')
    email = data.get('email')
    phone = data.get('phone')
    message = data.get('message')
    
    if not full_name or not email:
        return jsonify({"error": "Name and Email are required fields"}), 400
        
    try:
        conn = psycopg2.connect(DB_URI)
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO customer_submissions (full_name, email, phone_number, message)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """
        cursor.execute(insert_query, (full_name, email, phone, message))
        record_id = cursor.fetchone()[0]
        conn.commit()
        
        return jsonify({"success": True, "recordId": record_id}), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "This email has already been submitted."}), 400
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({"error": "Internal database capture error."}), 500
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
