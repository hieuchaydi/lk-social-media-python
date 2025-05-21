 lk - Ứng dụng mạng xã hội mini với Flask

![lk Logo](assets/logo.png)

lk là một ứng dụng mạng xã hội mini được phát triển bằng Python và Flask. Ứng dụng hỗ trợ đăng nhập bằng Google, đăng bài viết có ảnh, kết bạn, bình luận, nhắn tin thời gian thực và gọi video.

---
[![Live Demo](https://img.shields.io/badge/Demo-Live%20Site-brightgreen)](https://lk-5db7.onrender.com)
![Render Status](https://img.shields.io/website?down_message=offline&label=Render&up_message=online&url=https%3A%2F%2Flk-5db7.onrender.com)

**🌐 Truy cập ứng dụng ngay:** [https://lk-5db7.onrender.com](https://lk-5db7.onrender.com)

## Các chức năng chính

### 1. Đăng nhập / Đăng ký (Login / Register)
- Hỗ trợ đăng nhập bằng Google OAuth 2.0 với ảnh đại diện người dùng
- Callback URL: `https://yourdomain.com/google/callback`
- Đăng ký tài khoản thông thường với xác thực email

![Đăng nhập](assets/dangnhapgoogle.png)
![Đăng ký](assets/dangki.png)

### 2. Trang cá nhân (Profile)
- Quản lý thông tin cá nhân và ảnh đại diện
- Xem bài viết và bạn bè
- Thống kê tương tác

![Trang cá nhân](assets/profile.png)

### 3. Bảng tin (News Feed)
- Hiển thị bài viết theo thuật toán
- Tương tác like/comment
- Bài viết nổi bật

![Bảng tin](assets/newsfeed.png)

### 4. Đăng bài viết (Create Post)
- Đăng bài với hình ảnh và nội dung
- Định dạng bài viết phong phú
- Tag bạn bè

![Đăng bài](assets/dangbai.png)

### 5. Tương tác bài viết
- Bình luận và trả lời bình luận
- Biểu tượng cảm xúc

![Bình luận](assets/binhluan.png)

### 6. Kết bạn (Friends)
- Tìm kiếm bạn bè
- Gửi lời mời kết bạn
- Quản lý danh sách bạn bè

![Danh sách bạn](assets/danhsachban.png)
![Lời mời kết bạn](assets/loimoiketban.png)

### 7. Nhắn tin (Messaging)
- Chat real-time với bạn bè
- Gửi hình ảnh và file
- Thông báo tin nhắn mới

![Nhắn tin](assets/nhantin.png)

### 8. Gọi video (Video Call)
- Gọi video trực tiếp với bạn bè
- Chất lượng HD
- Tính năng chia sẻ màn hình

![Gọi điện](assets/goidien.png)

### 9. Tìm kiếm (Search)
- Tìm kiếm bài viết
- Tìm kiếm người dùng
- Bộ lọc nâng cao

![Tìm kiếm](assets/timkiem.png)
![Tìm bạn](assets/timkiembanthan.png)


### 10. quản lý
- trang quản lý
![Quản lý](assets/quanli.png)
- quản lý bài viết
![bài viết](assets/quanlibaiviet.png)
- quản lý bình luận
![Bình luận](assets/quanlybinhluan.png)






### Cài đặt

1. Clone repo:
    ```bash
    git clone <[repository-url](https://github.com/hieuchaydi/lk-social.git)>
    cd lk-social
    ```




### 2. (Tuỳ chọn) Tạo môi trường ảo

```bash
python -m venv venv
# Kích hoạt môi trường ảo:
source venv/bin/activate    # macOS / Linux
venv\Scripts\activate       # Windows
```

### 3. Cài đặt thư viện phụ thuộc

```bash
pip install -r requirements.txt
```

---

## 🗃️ Migrate database

```bash
flask db init
flask db migrate -m "Tạo cấu trúc database ban đầu"
flask db upgrade
```

> ⚠️ Nếu đã init database rồi thì **không cần chạy lại** `flask db init`.

---

## 🚀 Chạy ứng dụng

Bạn có thể chạy ứng dụng theo 1 trong 2 cách sau:

### ✅ Cách 1: Chạy bằng `python run.py`

```bash
python run.py
```

### ✅ Cách 2: Chạy bằng `flask run`

```bash
flask run --host=0.0.0.0 --port=5000
```

---

## ✅ Hoàn tất

Sau khi chạy, mở trình duyệt và truy cập:

```
http://localhost:5000/
```

---



**Cảm ơn bạn đã sử dụng lk!**
