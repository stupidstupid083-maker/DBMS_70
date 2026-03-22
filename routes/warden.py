from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from services.db import get_cursor
from functools import wraps

bp = Blueprint('warden', __name__, url_prefix='/warden')


def warden_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'warden':
            flash('Please log in as a warden.', 'warning')
            return redirect(url_for('auth.login', role='warden'))
        return f(*args, **kwargs)
    return decorated


@bp.route('/dashboard')
@warden_required
def dashboard():
    cursor = get_cursor()

    cursor.execute("SELECT COUNT(*) AS cnt FROM students")
    total_students = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) AS cnt FROM complaints WHERE status = 'pending'")
    pending_complaints = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) AS cnt FROM leave_pass WHERE status = 'pending'")
    pending_leaves = cursor.fetchone()['cnt']

    cursor.execute("""
        SELECT COALESCE(SUM(quantity_kg), 0) AS total FROM food_wastage WHERE date = date('now')
    """)
    food_today = cursor.fetchone()['total'] or 0

    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN status='present' THEN 1 ELSE 0 END), 0) AS present_count,
            COALESCE(SUM(CASE WHEN status='absent' THEN 1 ELSE 0 END), 0) AS absent_count
        FROM attendance WHERE date = date('now')
    """)
    attendance_today = cursor.fetchone()

    cursor.execute("""
        SELECT c.id, u.full_name, s.room_number, c.title, c.category, c.status, c.created_at
        FROM complaints c
        JOIN users u ON c.student_id = u.id
        LEFT JOIN students s ON u.id = s.user_id
        WHERE c.status != 'resolved'
        ORDER BY CASE WHEN c.status IN ('pending', 'unresolved') THEN 1 WHEN c.status = 'in_progress' THEN 2 ELSE 3 END,
                 c.created_at DESC LIMIT 10
    """)
    complaints = cursor.fetchall()

    cursor.execute("""
        SELECT lp.id, u.full_name, lp.from_date, lp.to_date, lp.reason, lp.status
        FROM leave_pass lp JOIN users u ON lp.student_id = u.id
        WHERE lp.status = 'pending' ORDER BY lp.created_at ASC LIMIT 10
    """)
    leaves = cursor.fetchall()

    return render_template('warden_dashboard.html',
        total_students=total_students, pending_complaints=pending_complaints,
        pending_leaves=pending_leaves, food_today=food_today,
        attendance_today=attendance_today, complaints=complaints, leaves=leaves)


@bp.route('/students')
@warden_required
def students():
    cursor = get_cursor()
    cursor.execute("""
        SELECT u.full_name, u.email, s.roll_number, s.course, s.year,
               s.room_number, s.phone,
               COALESCE(s.allergies, 'None') AS allergies
        FROM users u JOIN students s ON u.id = s.user_id
        ORDER BY s.roll_number
    """)
    students = cursor.fetchall()
    return render_template('students_list.html', students=students)


@bp.route('/student-profiles')
@warden_required
def student_profiles():
    cursor = get_cursor()

    # Filter params
    allergy_filter = request.args.get('allergy', '').strip()
    sleep_filter   = request.args.get('sleep', '').strip()
    social_filter  = request.args.get('social', '').strip()

    query = """
        SELECT u.full_name, u.email, s.roll_number, s.course, s.room_number,
               COALESCE(s.allergies, 'None') AS allergies,
               rp.q1 AS sleep_schedule, rp.q2 AS study_env,
               rp.q3 AS cleanliness,   rp.q4 AS social_pref
        FROM users u
        JOIN students s ON u.id = s.user_id
        LEFT JOIN roommate_profiles rp ON u.id = rp.student_id
        WHERE u.role = 'student'
    """
    params = []

    if allergy_filter:
        query += " AND LOWER(COALESCE(s.allergies,'')) LIKE ?"
        params.append(f'%{allergy_filter.lower()}%')
    if sleep_filter:
        query += " AND rp.q1 = ?"
        params.append(str(int(sleep_filter)))
    if social_filter:
        query += " AND rp.q4 = ?"
        params.append(str(int(social_filter)))

    query += " ORDER BY s.roll_number"

    cursor.execute(query, params)
    profiles = cursor.fetchall()

    return render_template('warden/student_profiles.html',
                           profiles=profiles,
                           allergy_filter=allergy_filter,
                           sleep_filter=sleep_filter,
                           social_filter=social_filter)
