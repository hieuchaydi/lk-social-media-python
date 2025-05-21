import os

class Config:
    SECRET_KEY = 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../instance/aihub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None
    ADMIN_USERNAME = 'admin'
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'Admin@123'  # Mật khẩu mạnh, có thể thay đổi
    
#flask run --host=0.0.0.0 --port=5000          
"""python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate """