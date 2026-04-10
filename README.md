# ABODE-Smart Hostel System 

A complete digital hostel management solution built with **Flask**, **MySQL**, and **HTML/CSS/JavaScript**.

# Project Members
1.Anika Singh Bisht-RA2411030030069

2.Palak Behune-RA2411030030070

## 📁 Project Documents

| Sr | Description                                  | Link |
|----|----------------------------------------------|------|
| 1  | Project Code                                | [View](#) |
| 2  | Project Report                              | [View](#) |
| 3  | Final PPT                                   | [View](#) |
| 4  | RA2411030030069_Certificate                 | [View](#) |
| 5  | RA2411030030070_Certificate                 | [View](#) |
| 6  | RA2411030030069_CourseReport                | [View](#) |
| 7  | RA2411030030070_CourseReport                | [View](#) |



## Features

| Module | Description |
|--------|-------------|
| 🔐 **Authentication** | Student & Warden login/register with hashed passwords |
| 📋 **Complaints** | Submit, track, and manage maintenance/food/security complaints |
| 📅 **Attendance** | Wardens mark daily attendance; students view their records |
| 🚪 **Leave Pass** | Apply for leave digitally; wardens approve/reject with remarks |
| 🍽️ **Food Wastage** | Log & track daily meal wastage with weekly summaries |
| 🔔 **Notifications** | Broadcast & targeted notifications system |
| 👷 **Workers** | Track maintenance staff availability |

## Tech Stack

- **Backend:** Python Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **Auth:** Werkzeug (password hashing)

## Quick Setup

### 1. Prerequisites
- Python 3.8+
- MySQL Server running locally

### 2. Create Database
```bash
mysql -u root -p < database/schema.sql
```

### 3. Configure Database
Edit `config.py` and set your MySQL password:
```python
MYSQL_PASSWORD = 'your_mysql_password'
```

### 4. Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Mac/Linux
pip install -r requirements.txt
```

### 5. Seed Sample Data
```bash
python seed_data.py
```

### 6. Run the App
```bash
python app.py
```
Open http://localhost:5000 in your browser.

## Demo Credentials

| Role | Username | Password |
|------|----------|----------|
| **Warden** | `warden_raj` | `Warden@123` |
| **Student** | `anika_bisht` | `Student@123` |

## Project Structure

```
SHMM/
├── app.py                 # Main Flask entry point
├── config.py              # Configuration (DB, secret key)
├── seed_data.py           # Seed script with sample data
├── requirements.txt       # Python dependencies
├── database/
│   └── schema.sql         # MySQL CREATE TABLE queries
├── services/
│   └── db.py              # MySQL connection helper
├── routes/
│   ├── auth.py            # Login / Register / Logout
│   ├── student.py         # Student dashboard
│   ├── warden.py          # Warden dashboard
│   ├── complaint.py       # Complaint CRUD
│   ├── attendance.py      # Attendance marking
│   ├── leave.py           # Leave pass management
│   ├── food.py            # Food wastage tracking
│   └── notification.py    # Notification system
├── templates/             # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── warden_dashboard.html
│   ├── complaint.html / complaint_form.html
│   ├── attendance.html
│   ├── leave_pass.html / leave_form.html
│   ├── food_wastage.html / food_form.html
│   ├── notifications.html / notification_form.html
│   └── students_list.html
└── static/
    ├── css/style.css
    └── js/main.js
```
