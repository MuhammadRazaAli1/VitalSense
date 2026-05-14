import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "trained_models")
os.makedirs(MODEL_DIR, exist_ok=True)


DIABETES_FEATURES = [
    ("Pregnancies", "Number of pregnancies", 0, 17, 1),
    ("Glucose", "Plasma glucose concentration (mg/dL)", 50, 250, 120),
    ("BloodPressure", "Diastolic blood pressure (mm Hg)", 40, 130, 70),
    ("SkinThickness", "Triceps skin fold thickness (mm)", 0, 60, 20),
    ("Insulin", "2-Hour serum insulin (mu U/ml)", 0, 600, 80),
    ("BMI", "Body Mass Index (kg/m^2)", 15.0, 60.0, 28.0),
    ("DiabetesPedigreeFunction", "Diabetes pedigree function", 0.05, 2.5, 0.5),
    ("Age", "Age (years)", 18, 90, 35),
]

HEART_FEATURES = [
    ("age", "Age (years)", 20, 90, 50),
    ("sex", "Sex (1 = male, 0 = female)", 0, 1, 1),
    ("cp", "Chest pain type (0-3)", 0, 3, 1),
    ("trestbps", "Resting blood pressure (mm Hg)", 80, 220, 130),
    ("chol", "Serum cholesterol (mg/dL)", 100, 600, 240),
    ("fbs", "Fasting blood sugar > 120 mg/dL (1/0)", 0, 1, 0),
    ("restecg", "Resting ECG result (0-2)", 0, 2, 1),
    ("thalach", "Maximum heart rate achieved", 60, 220, 150),
    ("exang", "Exercise induced angina (1/0)", 0, 1, 0),
    ("oldpeak", "ST depression by exercise", 0.0, 7.0, 1.0),
    ("slope", "Slope of peak exercise ST (0-2)", 0, 2, 1),
    ("ca", "Major vessels colored (0-3)", 0, 3, 0),
    ("thal", "Thalassemia (1=normal, 2=fixed, 3=reversible)", 1, 3, 2),
]

PARKINSONS_FEATURES = [
    ("MDVP_Fo", "Average vocal fundamental frequency (Hz)", 80.0, 270.0, 154.0),
    ("MDVP_Fhi", "Maximum vocal fundamental frequency (Hz)", 100.0, 600.0, 197.0),
    ("MDVP_Flo", "Minimum vocal fundamental frequency (Hz)", 60.0, 240.0, 116.0),
    ("MDVP_Jitter_pct", "Jitter percentage (%)", 0.0, 3.5, 0.6),
    ("MDVP_Jitter_Abs", "Jitter absolute (ms)", 0.0, 0.0003, 0.00004),
    ("MDVP_RAP", "Relative amplitude perturbation", 0.0, 0.03, 0.003),
    ("MDVP_PPQ", "Five-point period perturbation quotient", 0.0, 0.03, 0.003),
    ("Jitter_DDP", "Average absolute difference of differences", 0.0, 0.09, 0.009),
    ("MDVP_Shimmer", "Local shimmer", 0.0, 0.12, 0.03),
    ("MDVP_Shimmer_dB", "Local shimmer in dB", 0.0, 1.5, 0.28),
    ("Shimmer_APQ3", "Three-point amplitude perturbation quotient", 0.0, 0.06, 0.015),
    ("Shimmer_APQ5", "Five-point amplitude perturbation quotient", 0.0, 0.08, 0.018),
    ("MDVP_APQ", "Eleven-point amplitude perturbation quotient", 0.0, 0.15, 0.024),
    ("Shimmer_DDA", "Average absolute differences between consecutive amplitudes", 0.0, 0.18, 0.045),
    ("NHR", "Noise-to-harmonics ratio", 0.0, 0.5, 0.025),
    ("HNR", "Harmonics-to-noise ratio (dB)", 8.0, 35.0, 21.0),
    ("RPDE", "Recurrence period density entropy", 0.25, 0.7, 0.5),
    ("DFA", "Detrended fluctuation analysis", 0.55, 0.85, 0.72),
    ("spread1", "Nonlinear measure of fundamental frequency spread", -8.0, -2.0, -5.7),
    ("spread2", "Nonlinear measure 2", 0.0, 0.5, 0.23),
    ("D2", "Correlation dimension", 1.4, 3.7, 2.4),
    ("PPE", "Pitch period entropy", 0.04, 0.55, 0.21),
]


def _generate_diabetes_dataset(n=3000, seed=42):
    rng = np.random.RandomState(seed)
    pregnancies = rng.poisson(3, n).clip(0, 17)
    glucose = rng.normal(120, 32, n).clip(50, 250)
    bp = rng.normal(72, 13, n).clip(40, 130)
    skin = rng.normal(22, 12, n).clip(0, 60)
    insulin = rng.normal(85, 70, n).clip(0, 600)
    bmi = rng.normal(31, 7.5, n).clip(15, 60)
    dpf = rng.gamma(2.0, 0.3, n).clip(0.05, 2.5)
    age = rng.randint(18, 90, n)
    risk = (
        (glucose - 100) / 35
        + (bmi - 25) / 10
        + (age - 35) / 30
        + dpf * 1.2
        + (bp - 70) / 40
        + (pregnancies - 2) / 8
        + rng.normal(0, 0.6, n)
    )
    label = (risk > 1.4).astype(int)
    df = pd.DataFrame({
        "Pregnancies": pregnancies,
        "Glucose": glucose,
        "BloodPressure": bp,
        "SkinThickness": skin,
        "Insulin": insulin,
        "BMI": bmi,
        "DiabetesPedigreeFunction": dpf,
        "Age": age,
    })
    return df, label


def _generate_heart_dataset(n=3000, seed=43):
    rng = np.random.RandomState(seed)
    age = rng.randint(29, 78, n)
    sex = rng.binomial(1, 0.68, n)
    cp = rng.choice([0, 1, 2, 3], size=n, p=[0.5, 0.16, 0.28, 0.06])
    trestbps = rng.normal(131, 17, n).clip(80, 220)
    chol = rng.normal(246, 51, n).clip(100, 600)
    fbs = rng.binomial(1, 0.15, n)
    restecg = rng.choice([0, 1, 2], size=n, p=[0.5, 0.48, 0.02])
    thalach = rng.normal(149, 23, n).clip(60, 220)
    exang = rng.binomial(1, 0.33, n)
    oldpeak = rng.gamma(1.5, 0.7, n).clip(0, 7)
    slope = rng.choice([0, 1, 2], size=n, p=[0.21, 0.46, 0.33])
    ca = rng.choice([0, 1, 2, 3], size=n, p=[0.58, 0.21, 0.13, 0.08])
    thal = rng.choice([1, 2, 3], size=n, p=[0.06, 0.55, 0.39])
    risk = (
        (age - 50) / 20
        + (sex - 0.5) * 0.7
        + (cp == 0) * 0.9 - (cp == 2) * 0.4
        + (trestbps - 120) / 40
        + (chol - 200) / 80
        + fbs * 0.3
        + (restecg == 1) * 0.2
        - (thalach - 150) / 30
        + exang * 1.0
        + oldpeak * 0.6
        - (slope == 2) * 0.4
        + ca * 0.7
        + (thal == 3) * 0.9
        + rng.normal(0, 0.7, n)
    )
    label = (risk > 0.6).astype(int)
    df = pd.DataFrame({
        "age": age, "sex": sex, "cp": cp, "trestbps": trestbps, "chol": chol,
        "fbs": fbs, "restecg": restecg, "thalach": thalach, "exang": exang,
        "oldpeak": oldpeak, "slope": slope, "ca": ca, "thal": thal,
    })
    return df, label


def _generate_parkinsons_dataset(n=2500, seed=44):
    rng = np.random.RandomState(seed)
    fo = rng.normal(154, 41, n).clip(80, 270)
    fhi = fo + rng.gamma(2, 20, n)
    flo = fo - rng.gamma(2, 20, n)
    jitter_pct = rng.gamma(1.5, 0.4, n).clip(0.05, 3.5)
    jitter_abs = jitter_pct * 1e-5 * rng.uniform(0.7, 1.3, n)
    rap = jitter_pct * 0.005 * rng.uniform(0.8, 1.2, n)
    ppq = jitter_pct * 0.005 * rng.uniform(0.8, 1.2, n)
    ddp = rap * 3
    shimmer = rng.gamma(2.0, 0.018, n).clip(0.005, 0.12)
    shimmer_db = shimmer * 9.5 * rng.uniform(0.85, 1.15, n)
    apq3 = shimmer * 0.5
    apq5 = shimmer * 0.6
    apq = shimmer * 0.8
    dda = apq3 * 3
    nhr = rng.gamma(1.0, 0.04, n).clip(0, 0.5)
    hnr = (28 - nhr * 30 + rng.normal(0, 3, n)).clip(8, 35)
    rpde = rng.normal(0.5, 0.1, n).clip(0.25, 0.7)
    dfa = rng.normal(0.72, 0.05, n).clip(0.55, 0.85)
    spread1 = rng.normal(-5.7, 1.1, n).clip(-8, -2)
    spread2 = rng.normal(0.23, 0.08, n).clip(0, 0.5)
    d2 = rng.normal(2.4, 0.4, n).clip(1.4, 3.7)
    ppe = rng.normal(0.21, 0.09, n).clip(0.04, 0.55)
    risk = (
        jitter_pct * 1.3
        + shimmer * 18
        + nhr * 4
        - (hnr - 21) / 6
        + (rpde - 0.5) * 3
        + (spread1 + 5.7) * -0.7
        + ppe * 4
        + rng.normal(0, 0.8, n)
    )
    label = (risk > 1.6).astype(int)
    df = pd.DataFrame({
        "MDVP_Fo": fo, "MDVP_Fhi": fhi, "MDVP_Flo": flo,
        "MDVP_Jitter_pct": jitter_pct, "MDVP_Jitter_Abs": jitter_abs,
        "MDVP_RAP": rap, "MDVP_PPQ": ppq, "Jitter_DDP": ddp,
        "MDVP_Shimmer": shimmer, "MDVP_Shimmer_dB": shimmer_db,
        "Shimmer_APQ3": apq3, "Shimmer_APQ5": apq5, "MDVP_APQ": apq,
        "Shimmer_DDA": dda, "NHR": nhr, "HNR": hnr,
        "RPDE": rpde, "DFA": dfa, "spread1": spread1, "spread2": spread2,
        "D2": d2, "PPE": ppe,
    })
    return df, label


def _train(generator, name, model_factory):
    df, y = generator()
    X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=7, stratify=y)
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", model_factory()),
    ])
    pipe.fit(X_train, y_train)
    acc = accuracy_score(y_test, pipe.predict(X_test))
    meta = {"model": pipe, "accuracy": float(acc), "feature_names": list(df.columns)}
    joblib.dump(meta, os.path.join(MODEL_DIR, f"{name}.joblib"))
    return meta


def _load_or_train(name, generator, model_factory):
    path = os.path.join(MODEL_DIR, f"{name}.joblib")
    if os.path.exists(path):
        try:
            return joblib.load(path)
        except Exception:
            pass
    return _train(generator, name, model_factory)


def get_diabetes_model():
    return _load_or_train(
        "diabetes",
        _generate_diabetes_dataset,
        lambda: RandomForestClassifier(n_estimators=220, max_depth=10, random_state=11),
    )


def get_heart_model():
    return _load_or_train(
        "heart",
        _generate_heart_dataset,
        lambda: GradientBoostingClassifier(n_estimators=220, max_depth=4, random_state=11),
    )


def get_parkinsons_model():
    return _load_or_train(
        "parkinsons",
        _generate_parkinsons_dataset,
        lambda: RandomForestClassifier(n_estimators=240, max_depth=12, random_state=11),
    )


def predict_disease(meta, feature_dict):
    model = meta["model"]
    feats = meta["feature_names"]
    X = pd.DataFrame([[feature_dict[f] for f in feats]], columns=feats)
    proba = float(model.predict_proba(X)[0, 1])
    pred = int(proba >= 0.5)
    return pred, proba


def warm_up_models():
    get_diabetes_model()
    get_heart_model()
    get_parkinsons_model()
