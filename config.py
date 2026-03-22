import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'shmm-super-secret-key-2024')
    # SQLite database file (no MySQL needed!)
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'smart_hostel.db')
    DEBUG = True
