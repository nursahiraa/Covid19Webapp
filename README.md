# Covid19Webapp

This is a web application for predicting COVID-19 cases using machine learning models.\
To visualise predictions, it integrates a **Django backend (Django REST Framework) with a Streamlit frontend**.

---

## **Features**

- Predict COVID-19 cases using **hybrid models** (Random Forest + LSTM).
- **Django REST API** for serving predictions.
- **Streamlit-based Frontend** for visualisation.
- **MySQL Database** to store actual and predicted values.

---

## **Prerequisites**

Ensure you have the following installed:

- **Python**: 3.9.20 → Check version:
  ```bash
  python --version
  ```
- **Django**: 4.2.16 → Verify with:
  ```bash
  python -m django --version
  ```
- **Streamlit**: 1.40.2 → Verify with:
  ```bash
  streamlit --version
  ```
- **MySQL**: 9.0.1 → Verify with:
  ```bash
  mysql --version
  ```
- **Virtual Environment (venv)** → Ensure `.venv` is activated:
  ```bash
  source .venv/bin/activate  # macOS/Linux
  .venv\Scripts\activate     # Windows
  ```
- **MySQL Database** (Ensure MySQL is installed and running)

---

## **Installation**

1. **Clone this repository:**

   ```bash
   git clone https://github.com/nursahiraa/Covid19Webapp.git
   cd Covid19Webapp
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the MySQL database:**

   - Create a new MySQL database.
   - Update `settings.py` with your database credentials.
   - Apply migrations:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

---

## **Running the Web App**

### **1 Start the Django backend**

```bash
python manage.py runserver
```

This will start the API at `http://127.0.0.1:8000/`

### **2 Run the Streamlit frontend**

```bash
streamlit run streamlit/app.py
```

This will launch the visualization dashboard.

---

## **API Endpoints**

Here are the main API endpoints provided by the Django backend:

| Method | Endpoint          | Description                       |
| ------ | ----------------- | --------------------------------- |
| `GET`  | `/predict/`       | Returns COVID-19 case predictions |
| `GET`  | `/current_cases/` | Retrieves current case data       |
