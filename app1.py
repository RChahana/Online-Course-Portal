from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='master19*',
        database='Course_Portal',
        cursorclass=pymysql.cursors.DictCursor
    )
def get_faculty_name_by_id(user_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_name FROM registeration WHERE user_id = %s", (user_id,))
        faculty = cursor.fetchone()
    connection.close()
    return faculty['user_name'] if faculty else None


@app.route('/')
def home():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
    connection.close()
    return render_template('index2.html', courses=courses)

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    password = request.form['password']

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM registeration WHERE user_id=%s AND password=%s", 
                      (user_id, password))
        user = cursor.fetchone()
    connection.close()

    if user:
        session['user_id'] = user_id
        session['user_name'] = user['user_name']
        
        if user_id.startswith('S'):
            return redirect(url_for('student_dashboard'))
        elif user_id.startswith('F'):
            return redirect(url_for('faculty_dashboard'))
        else:
            return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('home'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Modify query to also retrieve course_id
        cursor.execute("""
            SELECT c.course_id, c.course_title, sc.status
            FROM student_course sc
            JOIN courses c ON sc.course_id = c.course_id
            WHERE sc.student_id = %s
        """, (session['user_id'],))
        enrolled_courses = cursor.fetchall()
    connection.close()

    return render_template('dashboard.html', 
                         courses=enrolled_courses,
                         user_name=session['user_name'])


@app.route('/course_page/<course_id>')
def course_page(course_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Fetch course details
        cursor.execute("""
            SELECT c.course_title, cd.created_date, cd.end_date, cd.overall_rating, 
                   cd.topics_covered, cd.prerequisites, c.credits
            FROM courses c
            JOIN course_details cd ON c.course_id = cd.cd_id
            WHERE c.course_id = %s
        """, (course_id,))
        course_details = cursor.fetchone()

        # Fetch announcements related to this course
        cursor.execute("""
            SELECT a.announcement
            FROM announcement a
            JOIN announcement_course ac ON a.announcement_id = ac.A_id
            WHERE ac.course_id = %s
        """, (course_id,))
        announcements = cursor.fetchall()  # Fetch all matching announcements

        # Fetch evaluation pattern based on course credits
        cursor.execute("""
            SELECT e.pattern
            FROM evaluation e
            WHERE e.credits = %s
        """, (course_details['credits'],))  # Using the credits from course_details
        evaluation_pattern = cursor.fetchone()

    connection.close()

    if not course_details:
        flash('Course details not found.')
        return redirect(url_for('student_dashboard'))

    return render_template('course_page.html', course=course_details, announcements=announcements, evaluation=evaluation_pattern)
@app.route('/join_course')
def join_course():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Fetch all available courses
        cursor.execute("""
            SELECT * FROM courses
        """)
        available_courses = cursor.fetchall()

    connection.close()

    return render_template('join_course.html', courses=available_courses)

@app.route('/register_course/<course_id>', methods=['POST'])
def register_course(course_id):
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']  # Assuming you have the user ID stored in the session
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Insert registration into the student_course table
        cursor.execute("""
            INSERT INTO student_course (student_id, course_id, status)
            VALUES (%s, %s, 'Registered')
        """, (user_id, course_id))
        connection.commit()

    connection.close()

    # Redirect to the dashboard with a success message
    flash('Successfully registered for the course!', 'success')  # Use flash messaging
    return redirect(url_for('dashboard'))
@app.route('/faculty_dashboard')
def faculty_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    user_id = session['user_id']  # Get user ID from the session
    faculty_name = get_faculty_name_by_id(user_id)  # Fetch the faculty name using the user ID

    # Fetch courses handled by the faculty
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.course_id, c.course_title 
            FROM courses c
            JOIN faculty f ON c.faculty_id = f.faculty_id
            WHERE f.faculty_id = %s
        """, (user_id,))
        courses_handled = cursor.fetchall()
    connection.close()

    return render_template('faculty_dashboard.html', 
                           faculty_name=faculty_name,
                           courses=courses_handled)
@app.route('/view_feedback')
def view_feedback():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    # Get the faculty_id from the session (assuming user is a faculty member)
    faculty_id = session.get('user_id')

    # Fetch feedback for the courses handled by the faculty
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT f.feedback, f.rating, c.course_title
            FROM feedback f
            JOIN courses c ON f.course_id = c.course_id
            WHERE c.faculty_id = %s
        """, (faculty_id,))
        feedback_data = cursor.fetchall()
    
    connection.close()

    # Render the feedback page with the retrieved data
    return render_template('view_feedback.html', feedback_data=feedback_data)
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    # Get the administrator's user_id from the session
    admin_id = session.get('user_id')

    # Connect to the database
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Fetch the administrator's name from the database
        cursor.execute("""
            SELECT admin_name 
            FROM administrator
            WHERE admin_id = %s
        """, (admin_id,))
        admin_data = cursor.fetchone()

        # Fetch the courses managed by the administrator
        cursor.execute("""
            SELECT c.course_title, c.course_id
            FROM courses c
            JOIN admin_course ac ON c.course_id = ac.course_id
            WHERE ac.admin_id = %s
        """, (admin_id,))
        courses_managed = cursor.fetchall()

        # Fetch the faculty members managed by the administrator
        cursor.execute("""
            SELECT f.faculty_id, f.faculty_name
            FROM faculty f
            JOIN admin_faculty af ON f.faculty_id = af.faculty_id
            WHERE af.admin_id = %s
        """, (admin_id,))
        faculty_managed = cursor.fetchall()

    connection.close()

    # If no administrator is found, redirect back to home
    if not admin_data:
        flash('Administrator not found.')
        return redirect(url_for('home'))

    # Render the admin dashboard with admin_name, courses managed, and faculty managed
    return render_template('admin_dashboard.html', 
                           admin_name=admin_data['admin_name'],
                           courses_managed=courses_managed,
                           faculty_managed=faculty_managed)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)