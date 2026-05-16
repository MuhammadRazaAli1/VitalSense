import streamlit as st
from datetime import datetime
from st_supabase_connection import SupabaseConnection
from typing import Optional, List, Dict, Any

# Supabase Client core initialization
try:
    conn = st.connection("supabase", type=SupabaseConnection)
except Exception as e:
    st.error(f"Supabase Connection Error: {e}")
    conn = None

def create_user(full_name: str, username: str, email: str, password: str,
                age: Optional[int], gender: Optional[str],
                blood_group: Optional[str], contact: Optional[str]) -> Optional[int]:
    if not conn: return None
    try:
        user_data = {
            "full_name": full_name.strip(),
            "username": username.strip().lower(),
            "email": email.strip().lower(),
            "password_hash": password,  # UI handles checking or direct passing
            "age": age,
            "gender": gender,
            "blood_group": blood_group,
            "contact": contact,
            "created_at": datetime.utcnow().isoformat()
        }
        response = conn.table("users").insert(user_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
    except Exception as e:
        print(f"Registration Error: {e}")
        return None
    return None

def authenticate_user(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    if not conn: return None
    ident = identifier.strip().lower()
    field = "email" if "@" in ident else "username"
    try:
        response = conn.table("users").select("*").eq(field, ident).eq("password_hash", password).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
    except Exception as e:
        print(f"Auth Error: {e}")
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    if not conn: return None
    try:
        response = conn.table("users").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
    except Exception:
        return None
    return None

def update_user_profile(user_id: int, full_name: str, age: int, gender: str,
                        blood_group: str, contact: str) -> None:
    if not conn: return
    try:
        update_data = {
            "full_name": full_name,
            "age": age,
            "gender": gender,
            "blood_group": blood_group,
            "contact": contact
        }
        conn.table("users").update(update_data).eq("id", user_id).execute()
    except Exception as e:
        print(f"Profile Update Error: {e}")

def save_prediction(user_id: int, disease: str, inputs_json: str,
                    probability: float, risk_score: float, result: str,
                    advice: str) -> Optional[int]:
    if not conn: return None
    try:
        pred_data = {
            "user_id": user_id,
            "disease": disease,
            "inputs_json": inputs_json,
            "probability": float(probability),
            "risk_score": float(risk_score),
            "result": result,
            "advice": advice,
            "created_at": datetime.utcnow().isoformat()
        }
        # predictions ya health_history jo table bhi tum use kar rahy ho
        response = conn.table("predictions").insert(pred_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
    except Exception as e:
        print(f"Save Prediction Error: {e}")
    return None

def get_user_predictions(user_id: int, disease: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if not conn: return []
    try:
        query = conn.table("predictions").select("*").eq("user_id", user_id).order("created_at", desc=True)
        if disease:
            query = query.eq("disease", disease)
        if limit:
            query = query.limit(int(limit))
        response = query.execute()
        return response.data if response.data else []
    except Exception:
        return []

def get_latest_prediction(user_id: int, disease: str) -> Optional[Dict[str, Any]]:
    rows = get_user_predictions(user_id, disease=disease, limit=1)
    return rows[0] if rows else None

def get_previous_prediction(user_id: int, disease: str, before_id: int) -> Optional[Dict[str, Any]]:
    if not conn: return None
    try:
        response = conn.table("predictions").select("*").eq("user_id", user_id).eq("disease", disease).lt("id", before_id).order("id", desc=True).limit(1).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
    except Exception:
        return None
    return None

def delete_prediction(pred_id: int, user_id: int) -> None:
    if not conn: return
    try:
        conn.table("predictions").delete().eq("id", pred_id).eq("user_id", user_id).execute()
    except Exception:
        pass

def count_predictions(user_id: int) -> Dict[str, int]:
    if not conn: return {}
    try:
        rows = get_user_predictions(user_id)
        counts = {}
        for r in rows:
            d = r.get("disease")
            if d:
                counts[d] = counts.get(d, 0) + 1
        return counts
    except Exception:
        return {}
