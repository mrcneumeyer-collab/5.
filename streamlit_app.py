import streamlit as st
import psycopg2

st.set_page_config(page_title="Student Enrollment App", page_icon="🎓")

# 👇 ADD SIDEBAR HERE
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Students", "Courses", "Enrollments"]
)

def get_connection():
    return psycopg2.connect(st.secrets["DATABASE_URL"])


# 👇 DASHBOARD PAGE (your current app)
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


# 👇 PLACEHOLDER PAGES (you’ll build these next)
elif page == "Students":
    st.title("Students Page")

elif page == "Courses":
    st.title("Courses Page")

elif page == "Enrollments":
    st.title("Enrollments Page")