# Online Course Portal

## 📌 Project Overview
The **Online Course Portal** is a web-based platform that allows students to register for courses, access learning materials, interact with faculty, and receive feedback on their performance. Administrators manage courses, faculty, and student enrollment. This project aims to provide a seamless online learning experience with structured course management.

## 🚀 Features
### 🔹 User Roles
- **Student**: Browse and enroll in courses, access learning materials, and provide feedback.
- **Faculty**: Manage courses, view student enrollments, and receive feedback.
- **Administrator**: Manage courses, faculty, and students.

### 🔹 Functionalities
- **Course Enrollment**: Students can register for available courses.
- **Feedback System**: Students provide course feedback, which is visible to faculty.
- **Admin Dashboard**: Admins manage courses and faculty assignments.
- **Faculty Dashboard**: Faculty members can view assigned courses and student feedback.
- **Database Integration**: Secure and structured data management using MySQL.

## 🛠️ Tech Stack
- **Frontend**: HTML, CSS
- **Backend**: Python (Flask)
- **Database**: MySQL

## 📂 Database Schema
### 🔸 Tables:
- `student(student_id, name, email, password)`
- `faculty(faculty_id, faculty_name, institute_name)`
- `administrator(admin_id, admin_name)`
- `courses(course_id, course_title, credits, duration, language, faculty_id)`
- `admin_course(admin_id, course_id, announcement_id)`
- `admin_faculty(admin_id, faculty_id)`
- `feedback(feedback_id, course_id, student_id, rating, feedback)`

## 🔗 Setup Instructions
### 📌 Prerequisites
Ensure you have the following installed:
- Python 3.x
- MySQL
- Flask and required dependencies (`pip install -r requirements.txt`)




