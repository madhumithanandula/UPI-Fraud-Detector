# UPI Fraud Detector

A machine learning-powered web application that helps identify potentially fraudulent UPI transactions. This Flask-based project includes a user authentication system, transaction analysis with real-time fraud predictions, complaint registration, and transaction history tracking.

---

## Features

- User registration and login system with hashed passwords
- Fraud prediction using a trained Random Forest classification model
- One-hot encoding and feature scaling for transaction inputs
- Complaint form for suspicious transactions
- Transaction history dashboard for individual users
- Clean frontend using HTML, CSS, and Jinja templating

---

## Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS (Bootstrap), Jinja2
- **Database**: SQLite
- **Machine Learning**: Scikit-learn, Joblib
- **Others**: Git, GitHub

---

## Machine Learning Model

- Features used: amount, year, month, transaction type, payment gateway, merchant category, transaction state
- Preprocessing includes one-hot encoding and feature scaling
- Trained using a Random Forest classifier with approximately 92% accuracy
- Saved as `.pkl` files and loaded into the Flask application for real-time predictions

---

## Project Structure

upi-fraud-detector/
│
├── app.py # Main Flask application
├── config.py # App configurations and database URI
├── models.py # SQLAlchemy ORM models
├── requirements.txt # Python dependencies
├── UPI_Fraud_Detection.ipynb # Model training notebook
│
├── templates/ # HTML templates (home, login, register, etc.)
├── static/ # Optional: CSS, JS files
├── model/ # Saved model files (.pkl)
├── screenshots/ # Screenshot images for README


---

## Screenshots

### Welcome Page
![Home Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Welcome_page.png?raw=true)

### Register Page
![Login Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Register_page.png?raw=true)

### Login Page
![Login Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Login_page.png?raw=true)

### User Dashboard
![Prediction Result](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/User_dashboard.png?raw=true)

### Prediction Details Form 
![Transaction History](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Fraud_Detection_Details_Form.png?raw=true)

### Predicted Legitimate
![Complaint Form](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Predicted_legitimate.png?raw=true)

### Payment Initiation
![Login Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Payment_initiation.png?raw=true)

### Payment Successful
![Login Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Payment_successfull.png?raw=true)

### Predicted Fraud
![Login Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Predicted_fraud.png?raw=true)

### Complaint Raise
![Login Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Raise_complaint.png?raw=true)

### Transaction history
![Login Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Transaction_history.png?raw=true)

### Complaints list
![Login Page](https://github.com/madhumithanandula/UPI-Fraud-Detector/blob/main/Complaints_list.png?raw=true)

---

## How to Run

1. Clone the repository  
2. Navigate into the project directory  
3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Place your `.pkl` model files in the `model/` directory  
5. Run the Flask application:

    ```bash
    python app.py
    ```

6. Open your browser and go to:  
   `http://127.0.0.1:5000/`

---

## Future Improvements

- Integrate Razorpay’s API for real transaction simulation
- Add OTP/email verification for account and complaint security
- Build an admin dashboard for managing fraud reports
- Deploy the project to platforms like Heroku or Render

---

## Author

**N. V. S. Madhumitha**  
Email: [madhumithanandula123@gmail.com](mailto:madhumithanandula123@gmail.com)  
Location: Hyderabad, India  
GitHub: [github.com/madhumithanandula](https://github.com/madhumithanandula)  
LinkedIn: [linkedin.com/in/madhumitha-nandula](https://www.linkedin.com/in/madhumitha-nandula)

---

## License

This project is licensed under the [MIT License](LICENSE).
