# 🩺 MedicareAI: Multi-Disease Prediction Engine

**MedicareAI** is an advanced, AI-powered healthcare analytics platform designed to predict multiple life-threatening diseases with high accuracy. Built using Python and Streamlit, it leverages machine learning models to provide instant health insights.

---

## 🚀 Key Features
* **Diabetes Prediction:** Analyzes glucose levels, BMI, and other factors to assess risk.
* **Heart Disease Detection:** Evaluates cardiovascular metrics to predict potential heart issues.
* **Parkinson’s Disease Assessment:** Uses specialized vocal and physical data points for early detection.
* **Automated Dataset Generation:** Includes logic to generate synthetic clinical datasets for model training.
* **PDF Report Generation:** Users can download a detailed health report after prediction.
* **History Tracking:** Maintains a local database of previous health checks for recovery monitoring.

---

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **Frontend & Backend:** Streamlit
- **Machine Learning:** Scikit-learn (RandomForest, GradientBoosting)
- **Data Handling:** Pandas, Numpy
- **Model Serialization:** Joblib
- **Database:** SQLite

---

## 📁 Project Structure
```text
MedicareAI/
├── core/               # Backend logic, Database & ML Model training
├── interface/          # Streamlit UI components and screens
├── data_set/           # Generated CSV datasets for transparency
├── trained_models/     # Pre-trained .joblib model files
├── app.py              # Main entry point of the application
└── requirements.txt    # List of dependencies```


⚙️ Installation & Setup

Clone the repository:

`Bash`
`git clone https://github.com/YOUR_USERNAME/MedicareAI.git`
`cd MedicareAI`

Install dependencies:

`Bash`
`pip install -r requirements.txt`

Run the application:

`Bash`
`streamlit run app.py`

📊 Methodology

* The project follows a standard Data Science lifecycle:
* Data Generation/Collection: Synthetic clinical data is generated with realistic distributions.
* Preprocessing: Handling missing values (imputation) and scaling features.
* Training: Models are trained using Ensemble learning techniques.
* Persistence: Models are saved as .joblib files to ensure fast loading during production.

👤 Author

Muhammad Raza Ali Computer Science Student & Aspiring Data Scientist
Gojra, Punjab, Pakistan
