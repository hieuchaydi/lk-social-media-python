from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from config import Config
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash

# Khởi tạo các extension
db = SQLAlchemy()
migrate = Migrate()  
login_manager = LoginManager()
socketio = SocketIO()
oauth = OAuth()
csrf = CSRFProtect()

# Hàm khởi tạo ứng dụng Flask
# Tạo ứng dụng Flask và cấu hình các extension
# Đăng ký các blueprint
# Đăng ký các route và các hàm xử lý
# Đăng ký các hàm xử lý sự kiện
# Đăng ký các hàm xử lý sự kiện của Flask-SocketIO
# Đăng ký các hàm xử lý sự kiện của Flask-OAuth
# Đăng ký các hàm xử lý sự kiện của Flask-WTF CSRF
# Đăng ký các hàm xử lý sự kiện của Flask-Login
# Đăng ký các hàm xử lý sự kiện của Flask-Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    csrf.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)
    oauth.init_app(app)

    login_manager.login_view = 'main.login'

    from .routes import main, admin
    app.register_blueprint(main)
    app.register_blueprint(admin)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from flask_wtf.csrf import generate_csrf
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    # Tạo tài khoản admin mặc định nếu chưa tồn tại
    with app.app_context():
        db.create_all()  # Đảm bảo bảng cơ sở dữ liệu đã được tạo
        admin_user = User.query.filter_by(email=app.config['ADMIN_EMAIL']).first()
        if not admin_user:
            admin_user = User(
                username=app.config['ADMIN_USERNAME'],
                email=app.config['ADMIN_EMAIL'],
                password=generate_password_hash(app.config['ADMIN_PASSWORD']),
                is_admin=True,
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Tài khoản admin '{app.config['ADMIN_USERNAME']}' đã được tạo.")

    return app