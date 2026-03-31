import streamlit as st
import psycopg2

st.set_page_config(page_title="Student Enrollment App", page_icon="🎓")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Students", "Courses", "Enrollments"]
)

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])


# DASHBOARD
if page == "Dashboard":
    st.title("🎓 Student Enrollment App")
    st.write("Welcome! Use the sidebar to navigate between pages.")

    st.markdown("---")
    st.subheader("📊 Current Data")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM students10;")
        student_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM courses10;")
        course_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM student_courses10;")
        enrollment_count = cur.fetchone()[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Students", student_count)
        col2.metric("Courses", course_count)
        col3.metric("Enrollments", enrollment_count)

        st.markdown("---")
        st.subheader("📋 All Enrollments")

        cur.execute("""
            SELECT s.name, s.email, c.course_name, sc.enrolled_at
            FROM student_courses10 sc
            JOIN students10 s ON sc.student_id = s.id
            JOIN courses10 c ON sc.course_id = c.id
            ORDER BY sc.enrolled_at DESC;
        """)
        rows = cur.fetchall()

        if rows:
            st.table([
                {
                    "Student": r[0],
                    "Email": r[1],
                    "Course": r[2],
                    "Enrolled": r[3].strftime("%Y-%m-%d %H:%M")
                }
                for r in rows
            ])
        else:
            st.info("No enrollments yet. Add some students and courses, then enroll them!")

        cur.close()
        conn.close()

    except Exception as e:
        st.error(f"Database connection error: {e}")


# STUDENTS PAGE
elif page == "Students":
    st.title("👤 Add a New Student")

    with st.form("add_student_form"):
        name = st.text_input("Student Name")
        email = st.text_input("Student Email")
        submitted = st.form_submit_button("Add Student")

        if submitted:
            if name and email:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO students10 (name, email) VALUES (%s, %s);",
                        (name, email)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ Student '{name}' added successfully!")
                except psycopg2.errors.UniqueViolation:
                    st.error("⚠️ A student with that email already exists.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please fill in both fields.")

    st.markdown("---")
    st.subheader("Current Students")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM students10 ORDER BY name;")
        students = cur.fetchall()
        cur.close()
        conn.close()

        if students:
            st.table([
                {"ID": s[0], "Name": s[1], "Email": s[2]}
                for s in students
            ])
        else:
            st.info("No students yet.")
    except Exception as e:
        st.error(f"Error: {e}")


# COURSES PAGE
elif page == "Courses":
    st.title("📚 Add a New Course")

    with st.form("add_course_form"):
        course_name = st.text_input("Course Name")
        submitted = st.form_submit_button("Add Course")

        if submitted:
            if course_name:
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO courses10 (course_name) VALUES (%s);",
                        (course_name,)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"✅ Course '{course_name}' added successfully!")
                except psycopg2.errors.UniqueViolation:
                    st.error("⚠️ A course with that name already exists.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter a course name.")

    st.markdown("---")
    st.subheader("Current Courses")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, course_name FROM courses10 ORDER BY course_name;")
        courses = cur.fetchall()
        cur.close()
        conn.close()

        if courses:
            st.table([
                {"ID": c[0], "Course Name": c[1]}
                for c in courses
            ])
        else:
            st.info("No courses yet.")
    except Exception as e:
        st.error(f"Error: {e}")


# ENROLLMENTS PAGE
elif page == "Enrollments":
    st.title("📝 Enroll a Student in a Course")

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id, name FROM students10 ORDER BY name;")
        students = cur.fetchall()

        cur.execute("SELECT id, course_name FROM courses10 ORDER BY course_name;")
        courses = cur.fetchall()

        cur.close()
        conn.close()

        if not students:
            st.warning("No students found. Please add a student first.")
        elif not courses:
            st.warning("No courses found. Please add a course first.")
        else:
            student_options = {s[1]: s[0] for s in students}
            course_options = {c[1]: c[0] for c in courses}

            with st.form("enroll_form"):
                selected_student = st.selectbox("Select Student", options=list(student_options.keys()))
                selected_course = st.selectbox("Select Course", options=list(course_options.keys()))
                submitted = st.form_submit_button("Enroll")

                if submitted:
                    student_id = student_options[selected_student]
                    course_id = course_options[selected_course]
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO student_courses10 (student_id, course_id) VALUES (%s, %s);",
                            (student_id, course_id)
                        )
                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success(f"✅ '{selected_student}' enrolled in '{selected_course}'!")
                    except psycopg2.errors.UniqueViolation:
                        st.error("⚠️ This student is already enrolled in that course.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    except Exception as e:
        st.error(f"Error: {e}")