# 🩺 MedicareAI: Multi-Disease Prediction Engine

**MedicareAI** is an advanced, AI-powered healthcare analytics platform designed to predict multiple life-threatening diseases with high accuracy. Built using **Python** and **Streamlit**, it leverages sophisticated machine learning models to provide instant health insights and predictive analytics.


## 🚀 Key Features

* **Diabetes Prediction:** Analyzes glucose levels, BMI, and clinical factors to assess patient risk.
* **Heart Disease Detection:** Evaluates cardiovascular metrics to predict potential heart issues.
* **Parkinson’s Disease Assessment:** Uses specialized vocal and physical data points for early-stage detection.
* **Automated Dataset Generation:** Includes logic to generate synthetic clinical datasets for robust model training.
* **PDF Report Generation:** Securely generates and allows users to download detailed health reports.
* **History Tracking:** Maintains a local SQLite database of previous health checks for recovery monitoring.


## 🛠️ Tech Stack

- **Language:** Python 3.x
- **Frontend & Backend:** Streamlit
- **Machine Learning:** Scikit-learn (RandomForest, GradientBoosting)
- **Data Handling:** Pandas, Numpy
- **Model Serialization:** Joblib
- **Database:** SQLite
- **Report Engine:** FPDF2


## 📁 Project Structure

```text
MedicareAI/
├── core/                # Backend logic, Database & ML Model training
├── interface/           # Streamlit UI components and screen sections
├── data_set/            # Generated CSV datasets for transparency
├── trained_models/      # Pre-trained .joblib model files
├── app.py               # Main entry point of the application
└── requirements.txt     # Essential project dependencies

⚙️ Installation & Setup
Clone the repository:

Bash
git clone [https://github.com/APKA_USERNAME/MedicareAI.git](https://github.com/APKA_USERNAME/MedicareAI.git)
cd MedicareAI
Install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
streamlit run app.py
👤 Author
Muhammad Raza Ali Computer Science Student & Aspiring Data Scientist

Gojra, Punjab, Pakistan
