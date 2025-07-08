import time
from flask import Flask, request, render_template, url_for, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import json
import pandas as pd
import numpy as np
import os
from models import db, Transaction, Complaint, User
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = SECRET_KEY

db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

# Load model, scaler, and columns
MODEL_PATH = os.path.join("model", "upi_fraud_rf_model.pkl")
SCALER_PATH = os.path.join("model", "scaler.pkl")
COLUMNS_PATH = os.path.join("model", "model_columns.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
model_columns = joblib.load(COLUMNS_PATH)

def extract_groups(columns):
    base_fields = ['amount', 'Year', 'Month']
    transaction_types = sorted([c.replace("Transaction_Type_", "") for c in columns if c.startswith("Transaction_Type_")])
    payment_gateways = sorted([c.replace("Payment_Gateway_", "") for c in columns if c.startswith("Payment_Gateway_")])
    states = sorted([c.replace("Transaction_State_", "") for c in columns if c.startswith("Transaction_State_")])
    merchant_categories = sorted([c.replace("Merchant_Category_", "") for c in columns if c.startswith("Merchant_Category_")])
    
    return {
        "base": base_fields,
        "transaction_types": transaction_types,
        "payment_gateways": payment_gateways,
        "states": states,
        "merchant_categories": merchant_categories
    }

@app.route('/')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Calculate Dashboard Analytics
        total_transactions = Transaction.query.filter_by(user_id=user_id).count()
        total_complaints = Complaint.query.filter_by(user_id=user_id).count()
        total_fraud_detections = Transaction.query.filter_by(user_id=user_id, prediction='Fraudulent').count()
        # unresolved_complaints = Complaint.query.filter_by(user_id=user_id, status='Unresolved').count()
        unresolved_complaints = total_complaints

        return render_template('home.html', 
                               logged_in=True, 
                               current_user=User.query.get(user_id),
                               total_transactions=total_transactions, 
                               total_complaints=total_complaints,
                               total_fraud_detections=total_fraud_detections,
                               unresolved_complaints=unresolved_complaints)
    else:
        return render_template('home.html', logged_in=False)


@app.route('/predict-form')
def predict_form():
    groups = extract_groups(model_columns)
    return render_template('predict_form.html', groups=groups)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or Email already exists.", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        return dict(logged_in=True, current_user=User.query.get(user_id))
    return dict(logged_in=False)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        user_input = request.form.to_dict()
        # Generate a unique transaction ID (e.g., using timestamp)
        transaction_id = f"TXN{int(time.time() * 1000)}"

        # Prepare input_dict for model
        input_dict = {col: 0 for col in model_columns}
        input_dict["amount"] = float(user_input.get("amount", 0))
        input_dict["Year"] = int(user_input.get("Year", 0))
        input_dict["Month"] = int(user_input.get("Month", 0))

        # One-hot encode user selections
        input_dict[f"Transaction_Type_{user_input['transaction_type']}"] = 1
        input_dict[f"Payment_Gateway_{user_input['payment_gateway']}"] = 1
        input_dict[f"Transaction_State_{user_input['state']}"] = 1
        input_dict[f"Merchant_Category_{user_input['merchant_category']}"] = 1

        # Convert to DataFrame and scale
        input_df = pd.DataFrame([input_dict])
        input_scaled = pd.DataFrame(scaler.transform(input_df), columns=input_df.columns)

        # Predict fraud
        prediction = model.predict(input_scaled)[0]
        prob = model.predict_proba(input_scaled)[0][1]
        fraud_result = f"{'Fraudulent' if prediction == 1 else 'Legitimate'} Transaction (Confidence: {prob:.2%})"

        if prediction == 1:
            # Fraudulent case: Block transaction and trigger complaint workflow
            recovery_result = "❌ Not recoverable (fraudulent transaction)."
            allow_transaction = False
            action_result = "Block transaction and raise complaint."
        else:
            # Legitimate case: Proceed, but flag as unclear
            recovery_result = "✅ Transaction recoverable (no fraud detected)."
            allow_transaction = True
            action_result = "Proceed, but flag as unclear."
        user_id = session.get("user_id")
        new_transaction = Transaction(
            transaction_id=transaction_id,
            amount=input_dict["amount"],
            year=input_dict["Year"],
            month=input_dict["Month"],
            transaction_type=user_input['transaction_type'],
            payment_gateway=user_input['payment_gateway'],
            state=user_input['state'],
            merchant_category=user_input['merchant_category'],
            prediction='Fraudulent' if prediction == 1 else 'Legitimate',
            confidence=prob,
            user_id=user_id if user_id else None
        )
        db.session.add(new_transaction)
        db.session.commit()

        return render_template("result.html",
                               result=fraud_result,
                               recovery=recovery_result,
                               action=action_result,
                               allow_transaction=allow_transaction,
                               input_data=user_input,
                               transaction_id=transaction_id,
                               )

    except Exception as e:
        return render_template("result.html",
                               result=f"Error: {str(e)}",
                               recovery=None,
                               action=None,
                               allow_transaction=False,
                               input_data={})
    
@app.route('/initiate_payment', methods=['POST'])
def initiate_payment():
    payment_data = request.form.to_dict()
    return render_template("payment_confirmation.html", payment_data=payment_data)

@app.route('/payment_details', methods=['POST'])
def payment_details():
    transaction_data = request.form.to_dict()
    return render_template("payment_details.html", transaction_data=transaction_data)

@app.route('/complaint/<transaction_id>', methods=['GET', 'POST'])
def complaint_form(transaction_id=None):
    # Get the current logged-in user's ID from the session
    user_id = session.get("user_id")
    
    # Handle the case when GET request is made
    if transaction_id:
        # Fetch the transaction details using transaction_id for the logged-in user
        transaction_details = Transaction.query.filter_by(transaction_id=transaction_id, user_id=user_id).first()
        if transaction_details:
            transaction_details = {
                "Transaction ID": transaction_details.transaction_id,
                "Amount": transaction_details.amount,
                "Year": transaction_details.year,
                "Month": transaction_details.month,
                "Transaction Type": transaction_details.transaction_type,
                "Payment Gateway": transaction_details.payment_gateway,
                "State": transaction_details.state,
                "Merchant Category": transaction_details.merchant_category,
            }
        else:
            transaction_details = {}
    else:
        transaction_details = {}

    # Fetch all transactions for the logged-in user for the dropdown
    transactions = Transaction.query.filter_by(user_id=user_id).all()  # Filter by user_id
    return render_template('complaint_form.html', 
                           transactions=transactions, 
                           transaction_details=transaction_details, 
                           from_home=request.args.get('from_home', False))


@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    try:
        user_id = session.get("user_id")
        transaction_id = request.form.get("transaction_id")

        # Basic validation
        if not transaction_id:
            flash("Transaction ID is missing. Please try again.", "danger")
            return redirect(url_for('home'))

        # Optional: Check if complaint for this transaction already exists
        existing = Complaint.query.filter_by(transaction_id=transaction_id, user_id=user_id).first()
        if existing:
            flash("A complaint for this transaction already exists.", "warning")
            return redirect(url_for('my_complaints'))

        # Parse the hidden JSON field
        transaction_details_raw = request.form.get("transaction_details", "{}")
        try:
            transaction_details_parsed = json.loads(transaction_details_raw)
        except Exception as e:
            flash("Failed to parse transaction details.", "danger")
            return redirect(url_for('home'))

        # Create a new complaint
        new_complaint = Complaint(
            transaction_id=transaction_id,
            name=request.form.get("name"),
            email=request.form.get("email"),
            complaint_details=request.form.get("complaint_details"),
            transaction_details=json.dumps(transaction_details_parsed),  # store as JSON string
            user_id=user_id if user_id else None
        )
        db.session.add(new_complaint)
        db.session.commit()

        flash("Complaint submitted successfully!", "success")
        return redirect(url_for('my_complaints'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('home'))

@app.route('/my-complaints')
def my_complaints():
    if 'user_id' not in session:
        flash("Please log in to view your complaints.", "warning")
        return redirect(url_for('login'))

    complaints = Complaint.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_complaints.html', complaints=complaints)

@app.route('/transaction_history')
def transaction_history():
    if 'user_id' not in session:
        flash("You need to log in first.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_transactions = Transaction.query.filter_by(user_id=user_id).all()

    return render_template('transaction_history.html', transactions=user_transactions)


if __name__ == '__main__':
    app.run(debug=True)
