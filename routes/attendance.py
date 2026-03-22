from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from services.db import get_cursor, commit_db
from datetime import date
from functools import wraps

bp = Blueprint('attendance', __name__, url_prefix='/attendance')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@bp.route('/')
@login_required
def view():
    cursor = get_cursor()
    uid = session['user_id']
    role = session['role']

    if role == 'warden':
        cursor.execute("""
            SELECT u.id AS user_id, u.full_name, s.roll_number, s.room_number,
                   a.date, a.status
            FROM users u
            JOIN students s ON u.id = s.user_id
            LEFT JOIN attendance a ON u.id = a.student_id AND a.date = date('now')
            ORDER BY s.roll_number
        """)
        records = cursor.fetchall()
        return render_template('attendance.html', records=records, role='warden', today=date.today())
    else:
        cursor.execute("""
            SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date DESC LIMIT 30
        """, (uid,))
        records = cursor.fetchall()
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN status='present' THEN 1 ELSE 0 END), 0) AS present,
                COALESCE(SUM(CASE WHEN status='absent' THEN 1 ELSE 0 END), 0) AS absent,
                COUNT(*) AS total
            FROM attendance WHERE student_id = ? AND date >= date('now', '-30 days')
        """, (uid,))
        summary = cursor.fetchone()
        return render_template('attendance.html', records=records, role='student', summary=summary)


@bp.route('/mark', methods=['POST'])
@login_required
def mark():
    if session.get('role') != 'warden':
        flash('Only wardens can mark attendance.', 'danger')
        return redirect(url_for('attendance.view'))

    student_ids = request.form.getlist('student_ids[]')
    statuses    = request.form.getlist('statuses[]')
    marked_by   = session['user_id']
    today       = str(date.today())

    cursor = get_cursor()
    for sid, status in zip(student_ids, statuses):
        cursor.execute("""
            INSERT INTO attendance (student_id, date, status, marked_by)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, date) DO UPDATE SET status = excluded.status, marked_by = excluded.marked_by
        """, (sid, today, status, marked_by))

    commit_db()
    flash(f"Attendance marked for {len(student_ids)} students.", 'success')
    return redirect(url_for('attendance.view'))
