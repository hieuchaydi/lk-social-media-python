# lk - Mini Social Media Application with Flask

![Logo lk](assets/logo.png)

**lk** is a lightweight social media application developed with **Python** and **Flask**. The app supports features such as Google OAuth login, post sharing with images, friend system, real-time messaging, and video calling.

---

[![Live Demo](https://img.shields.io/badge/Demo-Truy%20cập%20trực%20tiếp-brightgreen)](https://lk-5db7.onrender.com)
![Render Status](https://img.shields.io/website?down_message=offline&label=Render&up_message=online&url=https%3A%2F%2Flk-5db7.onrender.com)

🌐 **Access now:** [https://lk-5db7.onrender.com](https://lk-5db7.onrender.com)

## ✨ Main Features

### 1. Login / Signup
- **Login/Signup**: Sign in with Google OAuth 2.0 (with avatar) or register via email authentication.
- Google Callback URL: `http://127.0.0.1:5000/google/callback`

  ![Login](assets/dangnhapgoogle.png)  
  ![Signup](assets/dangki.png)

### 2. Profile Page
- Manage personal information and avatar.
- View posts and friend list.
- Interaction statistics.

  ![Profile Page](assets/profile.png)

### 3. News Feed
- Display posts using an algorithmic feed.
- Like and comment interactions.
- Featured posts.

  ![News Feed](assets/newsfeed.png)

### 4. Create Posts
- Share posts with images and rich text formatting.
- Tag friends in posts.

  ![Create Post](assets/dangbai.png)

### 5. Interact with Posts
- Comment and reply to comments.
- Use emoji reactions.

  ![Comment](assets/binhluan.png)

### 6. Friends System
- Search for friends.
- Send and manage friend requests.
- View friend list.

  ![Friend List](assets/danhsachban.png)  
  ![Friend Requests](assets/loimoiketban.png)

### 7. Messaging
- Real-time chat with friends.
- Send images and files.
- New message notifications.

  ![Messaging](assets/nhantin.png)

### 8. Video Call
- Direct video calls with friends.
- HD video quality.
- Screen sharing feature.

  ![Video Call](assets/goidien.png)

### 9. Search
- Search posts and users.
- Advanced search filters.

  ![Search](assets/timkiem.png)  
  ![Find Friends](assets/timkiembanthan.png)

### 10. Administration
- Admin dashboard to manage content.
- Manage posts and comments.

  ![Admin Dashboard](assets/quanli.png)  
  ![Manage Posts](assets/quanlibaiviet.png)  
  ![Manage Comments](assets/quanlybinhluan.png)

---

## 🛠️ Installation Guide

### 1. Download Source Code
```bash
git clone https://github.com/hieuchaydi/lk-social-media-python.git
cd lk-social-media-python
```

### 2. (Optional) Create a Virtual Environment
```bash
python -m venv venv
# Activate the virtual environment:
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
flask db init
flask db migrate -m "Initial database structure"
flask db upgrade
```

> ⚠️ **Note**: Skip `flask db init` if the database has already been initialized.

### 5. Run the Application
Choose one of the two methods:

#### Method 1: Use `run.py`
```bash
python run.py
```

#### Method 2: Use Flask CLI
```bash
flask run --host=0.0.0.0 --port=5000
```

### 6. Access the App
Open your browser and visit:
```
http://localhost:5000/
```

---

## 🔑 Google OAuth Setup

### 1. Create a Project on Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project:
   - Click the dropdown menu in the top left corner → **New Project**.
3. Go to **APIs & Services** > **OAuth consent screen**:
   - Choose **External** as user type.
   - Provide information:
     - **App name**: `My Flask App`
     - **User support email**: `your_email@gmail.com`
     - **Developer contact email**: `your_email@gmail.com`
     - **Logo**: (Optional)
   - Add **Authorized domains**: `127.0.0.1`
   - Add **Scopes**:
     - `email`
     - `profile`
     - `openid`
   - Save your settings.

### 2. Create OAuth Client ID
1. Go to **APIs & Services** > **Credentials**.
2. Click **Create Credentials** → **OAuth Client ID**.
3. Select **Web application** as the application type.
4. Add **Authorized redirect URI**:
   ```
   http://127.0.0.1:5000/google/callback
   ```
5. After creation, you will get:
   - **Client ID**: `your-client-id.apps.googleusercontent.com`
   - **Client Secret**: `your-client-secret`

### 3. Configure OAuth in the App
In `routes.py`, update your Google OAuth configuration with your information:
```python
google = oauth.register(
    name='google',
    client_id='your-client-id',
    client_secret='your-client-secret',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'consent',
        'access_type': 'offline'
    }
)
```

---
## 📚 References

📘 **Flask Documentation**  
🔗 [https://flask.palletsprojects.com/en/stable/](https://flask.palletsprojects.com/en/stable/)  
Official guide to building web apps with Flask.

🐍 **Python Documentation**  
🔗 [https://docs.python.org/3/](https://docs.python.org/3/)  
The official Python documentation with syntax, libraries, and examples.

## 🔐 Security

This project applies several basic security mechanisms:

- 🛡️ **CSRF Protection**: Uses `Flask-WTF` to protect the app from Cross-Site Request Forgery (CSRF) attacks.
- 🔑 **Password Hashing**: Uses the `bcrypt` library to securely hash user passwords before storing them in the database.

> ✅ These are important security steps to help protect users and the application from common vulnerabilities.

## 🙌 Thank You for Using lk!

If you encounter issues or have suggestions, please create an issue on the [GitHub repository](https://github.com/hieuchaydi/lk-social-media-python).
