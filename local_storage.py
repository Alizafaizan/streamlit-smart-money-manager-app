import json
import streamlit as st
from pathlib import Path

def save_local_data(username, data):
    """Save user data to local file"""
    data_dir = Path("user_data")
    data_dir.mkdir(exist_ok=True)
    
    file_path = data_dir / f"{username}_data.json"
    with open(file_path, "w") as f:
        json.dump(data, f)

def load_local_data(username):
    """Load user data from local file"""
    file_path = Path("user_data") / f"{username}_data.json"
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)
    return {
        "expenses": [],
        "income": 0
    }

def init_local_storage():
    """Initialize local storage directory"""
    data_dir = Path("user_data")
    data_dir.mkdir(exist_ok=True) 