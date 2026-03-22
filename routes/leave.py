from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from services.db import get_cursor, commit_db
from functools import wraps

bp = Blueprint('leave', __name__, url_prefix='/leave')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@bp.route('/')
@login_required
def list_leaves():
    cursor = get_cursor()
    uid  = session['user_id']
    role = session['role']

    if role == 'warden':
        cursor.execute("""
            SELECT lp.id, u.full_name, s.room_number, lp.from_date, lp.to_date,
                   lp.reason, lp.destination, lp.status, lp.created_at
            FROM leave_pass lp
            JOIN users u ON lp.student_id = u.id
            JOIN students s ON u.id = s.user_id
            ORDER BY CASE lp.status WHEN 'pending' THEN 0 ELSE 1 END, lp.created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT lp.id, lp.from_date, lp.to_date, lp.reason, lp.destination,
                   lp.status, lp.warden_remarks, lp.created_at
            FROM leave_pass lp WHERE lp.student_id = ? ORDER BY lp.created_at DESC
        """, (uid,))
    leaves = cursor.fetchall()
    return render_template('leave_pass.html', leaves=leaves, role=role)


@bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if session.get('role') != 'student':
        flash('Only students can apply for leave.', 'warning')
        return redirect(url_for('leave.list_leaves'))

    if request.method == 'POST':
        from_date   = request.form.get('from_date')
        to_date     = request.form.get('to_date')
        reason      = request.form.get('reason', '').strip()
        destination = request.form.get('destination', '').strip()
        uid         = session['user_id']

        if not all([from_date, to_date, reason]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('leave_form.html')

        cursor = get_cursor()
        cursor.execute(
            "INSERT INTO leave_pass (student_id, from_date, to_date, reason, destination) VALUES (?, ?, ?, ?, ?)",
            (uid, from_date, to_date, reason, destination)
        )
        commit_db()
        flash('Leave application submitted successfully!', 'success')
        return redirect(url_for('leave.list_leaves'))

    return render_template('leave_form.html')


@bp.route('/action/<int:leave_id>', methods=['POST'])
@login_required
def action(leave_id):
    if session.get('role') != 'warden':
        flash('Only wardens can approve or reject leave.', 'danger')
        return redirect(url_for('leave.list_leaves'))

    decision = request.form.get('decision')
    remarks  = request.form.get('remarks', '').strip()
    warden_id = session['user_id']

    cursor = get_cursor()
    cursor.execute("""
        UPDATE leave_pass
        SET status = ?, approved_by = ?, approved_at = datetime('now'), warden_remarks = ?
        WHERE id = ?
    """, (decision, warden_id, remarks, leave_id))
    commit_db()
    flash(f'Leave request {decision}.', 'success')
    return redirect(url_for('leave.list_leaves'))
