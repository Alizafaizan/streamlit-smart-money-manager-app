import yaml
from pathlib import Path
import streamlit as st
from yaml.loader import SafeLoader
import bcrypt

def load_config():
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def save_config(config):
    with open('config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def init_users():
    if not Path('config.yaml').exists():
        save_config({'users': {}})
    return load_config()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def create_user(username, password):
    config = load_config()
    if username not in config['users']:
        config['users'][username] = hash_password(password)
        save_config(config)
        return True
    return False

def authenticate(username, password):
    config = load_config()
    if username in config['users']:
        return check_password(password, config['users'][username])
    return False

def get_offline_users():
    """Get list of users who have local data"""
    data_dir = Path("user_data")
    users = []
    if data_dir.exists():
        for file in data_dir.glob("*_data.json"):
            username = file.stem.replace("_data", "")
            users.append(username)
    return users 
