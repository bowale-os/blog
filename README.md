# 📝 Flask Blog App

A dynamic, full-stack blog web application built with **Flask**, **SQLAlchemy**, and **Bootstrap**. Users can **register**, **log in**, **comment on posts**, and **explore blog content**. Admin users can **create**, **edit**, and **delete posts**. The app also includes a **contact form** that sends user messages via email.

## 🌐 Live Demo

[🔗 https://daniels-blog-88xl.onrender.com/](#)

---

## 📌 Features

* ✅ User Registration & Login (Secure password hashing with Werkzeug)
* ✅ Admin-only routes for post creation/editing/deletion
* ✅ CKEditor integration for rich blog content editing
* ✅ Comment system (only for logged-in users)
* ✅ Flask-Login for session management
* ✅ Responsive Bootstrap layout
* ✅ Contact form with email notifications using SMTP
* ✅ Gravatar support for user profile images

---

## 🗂️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** Jinja2 templates, HTML5, Bootstrap5, CKEditor
* **Database:** SQLite (default), SQLAlchemy ORM
* **Authentication:** Flask-Login
* **Email:** `smtplib`, Gmail SMTP
* **Deployment:** *Render*

---

## 📁 Directory Structure

```bash
.
├── main.py                  # Main application file
├── forms.py                # Flask-WTF forms
├── templates/              # HTML templates (Jinja2)
│   ├── xinde.html          # Home page
│   ├── post.html           # Single post view
│   ├── register.html       # Registration page
│   ├── login.html          # Login page
│   ├── contact.html        # Contact page
│   ├── make-post.html      # Post creation/editing
│   └── about.html          # About page
├── static/                 # Static assets (CSS, JS, images)
├── .env                    # Environment variables (not pushed to repo)
├── requirements.txt        # Dependencies
└── README.md               
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
FLASK_SECRET=your_secret_key
DATABASE_URI=sqlite:///blog.db  # Or your production database URI
APP_PASSWORD=your_app_password_for_email
email_recipient=recipient@example.com
```

> 📌 **Note:** For Gmail SMTP, generate an **App Password** if using 2FA.

---

## 🚀 Running Locally

### 1. Clone the Repository

```bash
git clone https://github.com/bowale-os/blog.git
cd blog
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file as shown above.

### 5. Run the App

```bash
python main.py
```

Visit `http://127.0.0.1:5002` in your browser.

---

## 👤 Admin Access

To access admin-only web routes:

* Register normally.
* The **first registered user** (ID = 1) becomes the admin.
* Admin can add, edit, and delete posts.

---

## 🧪 Testing Features

* **Commenting** requires registeration and login.
* **Email contact** can be tested by submitting the contact form.
* **Admin-only routes** are protected with a decorator (`@admin_only`).

---

## 📧 Contact & Feedback

For feedback or issues, feel free to open an issue or contact me directly.

---

## 📜 License

This project is licensed under the MIT License.
