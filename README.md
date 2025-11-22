# BIG-IN Community Events Portal

A Django-based event management system for **Admins**, **Organizers**, and **Attendees**.

---

## Overview

The **BIG-IN Community Events Portal** is a web application designed to manage and organize community events.  
It supports three main user roles with distinct permissions and dashboards:

### **Admin**
- Reviews and moderates organizer-submitted events  
- Manages users (admins, organizers, attendees)  
- Monitors platform-wide activity and feedback  

### **Organizer**
- Creates, edits, and deletes events  
- Manages event details such as schedule, venue, image, capacity, and status  
- Views attendees and feedback related to their events  

### **Attendee**
- Registers and logs in  
- Browses, filters, and joins events  
- Submits feedback and ratings from **1–5 stars** after attending  

The system includes full CRUD operations, user management, feedback handling, and dashboards optimized per role.

---

## Features

### **User Authentication**
- Login using username and password  
- Register an account (username, first name, last name, email, role, password, confirmation)  
- Forgot Password functionality  
- Role-based redirection after login (Admin, Organizer, Attendee)  

### **Admin**
- Dashboard with platform statistics  
- Approve or reject events  
- Manage users (create, edit, delete, deactivate)  
- View all events and their feedback  

### **Organizer**
- Create and manage events  
- Upload event images  
- View event attendees  
- View feedback and attendee ratings (1–5 stars)  
- Update profile  

### **Attendee**
- Browse and filter events  
- Join events and manage joined list  
- Submit feedback  
- Update profile
  
---

## Tech Stack

- **Python 3**
- **Django 5.2.8**
- **SQLite**
- **Bootstrap 5**
- **Pillow** (image handling)
- **Custom Django Seeder Command**

### Requirements (`requirements.txt`)
```
asgiref==3.10.0
Django==5.2.8
pillow==12.0.0
sqlparse==0.5.3
tzdata==2025.2
```

---

# Installation & Setup

### **1. Clone the repository**
```
git clone https://github.com/Nopd101/community_events_portal
cd community_events_portal
```

### **2. Create a virtual environment**

**Windows (PowerShell):**
```
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

### **3. Install dependencies**
```
pip install -r requirements.txt
```

### **4. Apply migrations**
```
python manage.py makemigrations
python manage.py migrate
```

### **5. Run seeders**
```
python manage.py seed_initial_data
```

### **6. Create a superuser**
```
python manage.py createsuperuser
```

### **7. Start the development server**
```
python manage.py runserver
```

Then open:  
http://127.0.0.1:8000/

---

# Custom Management Commands

## **seed_initial_data**

Seeds essential initial data for the system.

### This command performs the following:

- Creates default roles  
  - Admin  
  - Organizer  
  - Attendee  
- Sets permissions  
- Creates **6 initial users**  
  - 2 Admins  
  - 2 Organizers  
  - 2 Attendees  
- Creates **10 sample events**  
  - Each organizer receives 5 events  
  - Each set includes **3 Approved** and **2 Pending**  

### Run:
```
python manage.py seed_initial_data
```

---

# Authors / Contributors

**Ando, Miyuki Angel C.** – Frontend Developer  
**Cruz, John Daryl P.** – Backend Developer, Database Manager, Project Manager  
**Dela Cruz, John Luther F.** – Backend Developer, Database Manager  
**Eleazar, Jhon Ron P.** – Documentor / Tester  
**Eugenio Jr., Miguel B.** – Documentor / Tester  

---

# Notes

- `db.sqlite3` and `venv/` are intentionally ignored from Git.  
- Seeders must be run **after migrations**.  
- Each group member must create their **own superuser** for login.
