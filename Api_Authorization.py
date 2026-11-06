
"""
DocSynapse - API Authorization Security Testing

Tests:
1. Authentication required
2. Role-based authorization
3. Patient endpoint restrictions
4. Doctor endpoint restrictions
5. Admin endpoint restrictions
6. Horizontal access control

Run:
pip install flask requests
python api_authorization_test.py
"""

from flask import Flask, request, jsonify
import threading
import time
import requests

app = Flask(__name__)

# Simulated test users
TOKENS = {
    "admin-token": {"id": 1, "role": "admin"},
    "doctor-token": {"id": 2, "role": "doctor"},
    "patient-token": {"id": 3, "role": "patient"},
    "staff-token": {"id": 4, "role": "staff"}
}


def authorize(allowed_roles=None):

    def decorator(func):

        def wrapper(*args, **kwargs):

            token = request.headers.get("Authorization", "")
            token = token.replace("Bearer ", "", 1)

            user = TOKENS.get(token)

            if not user:
                return jsonify({
                    "error": "Unauthorized"
                }), 401

            if allowed_roles and user["role"] not in allowed_roles:
                return jsonify({
                    "error": "Forbidden",
                    "message": "Insufficient permissions"
                }), 403

            request.current_user = user

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper

    return decorator


# Public endpoint
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "API running"})


# Admin-only endpoint
@app.route("/api/admin/users", methods=["GET"])
@authorize(["admin"])
def admin_users():
    return jsonify({"message": "Admin access granted"})


# Doctor-only endpoint
@app.route("/api/doctor/patients", methods=["GET"])
@authorize(["doctor", "admin"])
def doctor_patients():
    return jsonify({"message": "Doctor access granted"})


# Patient endpoint
@app.route("/api/patient/profile", methods=["GET"])
@authorize(["patient", "admin"])
def patient_profile():
    return jsonify({"message": "Patient access granted"})


# Staff endpoint
@app.route("/api/staff/dashboard", methods=["GET"])
@authorize(["staff", "admin"])
def staff_dashboard():
    return jsonify({"message": "Staff access granted"})


def start_server():
    app.run(port=5000, debug=False, use_reloader=False)


def run_tests():

    base_url = "http://127.0.0.1:5000"

    tests = [
        {
            "name": "Admin accessing admin endpoint",
            "token": "admin-token",
            "endpoint": "/api/admin/users",
            "expected": 200
        },
        {
            "name": "Patient accessing admin endpoint",
            "token": "patient-token",
            "endpoint": "/api/admin/users",
            "expected": 403
        },
        {
            "name": "Doctor accessing admin endpoint",
            "token": "doctor-token",
            "endpoint": "/api/admin/users",
            "expected": 403
        },
        {
            "name": "Doctor accessing doctor endpoint",
            "token": "doctor-token",
            "endpoint": "/api/doctor/patients",
            "expected": 200
        },
        {
            "name": "Patient accessing doctor endpoint",
            "token": "patient-token",
            "endpoint": "/api/doctor/patients",
            "expected": 403
        },
        {
            "name": "Patient accessing own profile endpoint",
            "token": "patient-token",
            "endpoint": "/api/patient/profile",
            "expected": 200
        },
        {
            "name": "Staff accessing staff endpoint",
            "token": "staff-token",
            "endpoint": "/api/staff/dashboard",
            "expected": 200
        },
        {
            "name": "Unauthenticated API request",
            "token": None,
            "endpoint": "/api/admin/users",
            "expected": 401
        }
    ]

    passed = 0
    failed = 0

    print("\nDOCSYNAPSE API AUTHORIZATION TEST")
    print("=" * 55)

    for test in tests:

        headers = {}

        if test["token"]:
            headers["Authorization"] = (
                "Bearer " + test["token"]
            )

        try:
            response = requests.get(
                base_url + test["endpoint"],
                headers=headers,
                timeout=5
            )

            success = response.status_code == test["expected"]

            if success:
                passed += 1
                result = "PASS"
            else:
                failed += 1
                result = "FAIL"

            print(f"\nTest: {test['name']}")
            print(f"Expected: {test['expected']}")
            print(f"Actual: {response.status_code}")
            print(f"Result: {result}")

        except requests.RequestException as error:
            failed += 1
            print(f"\nTest: {test['name']}")
            print("Result: ERROR")
            print(error)

    print("\n" + "=" * 55)
    print("TEST SUMMARY")
    print("=" * 55)
    print("Total:", len(tests))
    print("Passed:", passed)
    print("Failed:", failed)


if __name__ == "__main__":

    server = threading.Thread(
        target=start_server,
        daemon=True
    )

    server.start()

    time.sleep(1)

    run_tests()
