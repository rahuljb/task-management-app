# Task Management Application

A Task Management Application built with Django and Django REST Framework, featuring
JWT authentication and a custom Admin Panel using HTML templates.

---

## Tech Stack
- Python
- Django
- Django REST Framework
- JWT Authentication (SimpleJWT)
- SQLite
- HTML (Django Templates)

---

## Features

### User API (JWT Protected)
- User authentication using JWT
- View assigned tasks
- Update task status
- Submit completion report and worked hours when completing tasks

### Admin Panel (Custom HTML)
- SuperAdmin can:
  - Create, update, delete users and admins
  - Assign roles (SuperAdmin / Admin / User)
  - Assign users to admins
  - View and manage all tasks
  - View task completion reports

- Admin can:
  - Assign tasks to their users
  - View and manage tasks assigned to their users
  - View task completion reports
  - Cannot manage user roles

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <REPOSITORY_URL>
cd task-management-app
