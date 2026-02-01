from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI')
client = None
db = None

if not MONGO_URI:
    print("Warning: MONGO_URI not found in environment variables.")
    # Fallback for local testing if needed, though production needs Atlas
    MONGO_URI = 'mongodb://localhost:27017/pec_leave_portal'

try:
    client = MongoClient(MONGO_URI)
    try:
        db = client.get_default_database()
    except Exception:
        db = client['pec_leave_portal']
    print(f"Connected to MongoDB: {db.name}")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    # Initialize a dummy db object or handle failure gracefully if critical
    # For now, we will just let it fail later if accessed, but the variable exists


# Collections
# Collections
if db is not None:
    students_col = db['students']
    advisors_col = db['advisors']
    hods_col = db['hods']
    management_col = db['management']
    leaves_col = db['leave_applications']
else:
    students_col = None
    advisors_col = None
    hods_col = None
    management_col = None
    leaves_col = None

# --- Helper Functions ---
def serialize_doc(doc):
    if not doc: return None
    doc['_id'] = str(doc['_id'])
    return doc

# --- Initialization Route (Optional: Seed Data) ---
@app.route('/api/seed', methods=['POST'])
def seed_data():
    # Only run if collections are empty to avoid duplicates
    if advisors_col.count_documents({}) == 0:
        default_advisors = [
            {'dept': 'CSC', 'id': 'csc_advisor', 'password': 'advisor123', 'name': 'Dr. Ravi Kumar'},
            {'dept': 'ECE', 'id': 'ece_advisor', 'password': 'advisor123', 'name': 'Dr. Priya Sharma'},
            {'dept': 'AI&ML', 'id': 'aiml_advisor', 'password': 'advisor123', 'name': 'Dr. Suresh Patel'},
            {'dept': 'CYBER', 'id': 'cyber_advisor', 'password': 'advisor123', 'name': 'Dr. Anjali Reddy'}
        ]
        advisors_col.insert_many(default_advisors)

    if hods_col.count_documents({}) == 0:
        default_hods = [
            {'dept': 'CSC', 'id': 'csc_hod', 'password': 'hod123', 'name': 'Dr. Karthik Rajan'},
            {'dept': 'ECE', 'id': 'ece_hod', 'password': 'hod123', 'name': 'Dr. Meena Iyer'},
            {'dept': 'AI&ML', 'id': 'aiml_hod', 'password': 'hod123', 'name': 'Dr. Arjun Menon'},
            {'dept': 'CYBER', 'id': 'cyber_hod', 'password': 'hod123', 'name': 'Dr. Neha Gupta'}
        ]
        hods_col.insert_many(default_hods)

    if management_col.count_documents({}) == 0:
        management_col.insert_one({'id': 'management', 'password': 'management123', 'name': 'College Management'})

    return jsonify({"message": "Database seeded with default staff credentials"}), 200

# --- Auth Routes ---

@app.route('/api/login/student', methods=['POST'])
def login_student():
    data = request.json
    reg_no = data.get('regNo')
    dob = data.get('dob')
    
    student = students_col.find_one({'regNo': reg_no, 'dob': dob})
    if student:
        return jsonify(serialize_doc(student)), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/login/staff', methods=['POST'])
def login_staff():
    data = request.json
    role = data.get('role') # advisor, hod, management
    user_id = data.get('id')
    password = data.get('password')
    dept = data.get('dept') # Optional, for advisor/hod

    user = None
    if role == 'advisor':
        user = advisors_col.find_one({'id': user_id, 'password': password, 'dept': dept})
    elif role == 'hod':
        user = hods_col.find_one({'id': user_id, 'password': password, 'dept': dept})
    elif role == 'management':
        user = management_col.find_one({'id': user_id, 'password': password})
    
    if user:
        return jsonify(serialize_doc(user)), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/login/admin', methods=['POST'])
def login_admin():
    data = request.json
    user_id = data.get('id')
    password = data.get('password')
    
    # Hardcoded admin for now, matching frontend logic
    if user_id == 'admin' and password == 'admin':
        return jsonify({'id': 'admin', 'name': 'Administrator'}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# --- Student Routes ---

@app.route('/api/students', methods=['GET', 'POST', 'DELETE'])
def manage_students():
    if request.method == 'GET':
        students = list(students_col.find())
        return jsonify([serialize_doc(s) for s in students])
    
    elif request.method == 'POST':
        # Handles both single add and bulk import
        data = request.json
        if isinstance(data, list): # Bulk import
            # Check for duplicates or use upsert logic if needed
            # For simplicity, inserting new ones. In prod, use bulk_write with upsert.
            if not data: return jsonify({"message": "No data"}), 400
            
            # Simple unique check (slow for large data, ok for demo)
            inserted_count = 0
            for s in data:
                if not students_col.find_one({'regNo': s['regNo']}):
                    students_col.insert_one(s)
                    inserted_count += 1
            return jsonify({"message": f"Imported {inserted_count} students"}), 201
            
        else: # Single add
            if students_col.find_one({'regNo': data['regNo']}):
                return jsonify({"error": "Student already exists"}), 409
            result = students_col.insert_one(data)
            return jsonify({"message": "Student created", "id": str(result.inserted_id)}), 201

    elif request.method == 'DELETE':
        reg_no = request.args.get('regNo')
        students_col.delete_one({'regNo': reg_no})
        return jsonify({"message": "Student deleted"}), 200

# --- Leave Routes ---

@app.route('/api/leaves', methods=['GET', 'POST'])
def leaves():
    if request.method == 'POST':
        data = request.json
        data['appliedDate'] = datetime.datetime.now().strftime('%Y-%m-%d')
        data['status'] = 'Pending'
        result = leaves_col.insert_one(data)
        
        # Update student contact info if changed
        students_col.update_one(
            {'regNo': data['regNo']},
            {'$set': {'email': data['studentEmail'], 'parentMobile': data['parentMobile']}}
        )
        
        return jsonify({"message": "Leave applied", "id": str(result.inserted_id)}), 201

    elif request.method == 'GET':
        # Filtering logic
        reg_no = request.args.get('regNo')
        dept = request.args.get('dept')
        status = request.args.get('status')
        
        query = {}
        if reg_no: query['regNo'] = reg_no
        if dept and dept != 'null': query['dept'] = dept
        if status: query['status'] = status
        
        leaves_list = list(leaves_col.find(query).sort('appliedDate', -1))
        return jsonify([serialize_doc(leave) for leave in leaves_list])

@app.route('/api/leaves/<leave_id>/status', methods=['PUT'])
def update_leave_status():
    data = request.json
    new_status = data.get('status')
    role = data.get('role') # advisor or hod
    
    update_fields = {'status': new_status}
    action_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    if role == 'advisor':
        update_fields['advisorAction'] = action_date
    elif role == 'hod':
        update_fields['hodAction'] = action_date
        
    leaves_col.update_one(
        {'_id': ObjectId(leave_id)},
        {'$set': update_fields}
    )
    return jsonify({"message": "Status updated"}), 200

# --- Data Management Routes ---

@app.route('/api/reset', methods=['POST'])
def reset_data():
    db.students.delete_many({})
    db.leave_applications.delete_many({})
    db.advisors.delete_many({})
    db.hods.delete_many({})
    db.management.delete_many({})
    # Re-seed default staff
    seed_data()
    return jsonify({"message": "All data reset"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
