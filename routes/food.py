from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from services.db import get_cursor, commit_db
from datetime import date
from functools import wraps

bp = Blueprint('food', __name__, url_prefix='/food')


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
    cursor.execute("""
        SELECT fw.id, fw.meal_type, fw.quantity_kg, fw.date, fw.notes, u.full_name AS logged_by_name
        FROM food_wastage fw
        LEFT JOIN users u ON fw.logged_by = u.id
        ORDER BY fw.date DESC, fw.meal_type ASC
        LIMIT 60
    """)
    records = cursor.fetchall()

    # Weekly summary
    cursor.execute("""
        SELECT date, SUM(quantity_kg) AS total_kg FROM food_wastage
        WHERE date >= date('now', '-7 days') GROUP BY date ORDER BY date DESC
    """)
    weekly = cursor.fetchall()

    cursor.execute("SELECT COALESCE(SUM(quantity_kg), 0) AS total FROM food_wastage WHERE date = date('now')")
    today_total = cursor.fetchone()['total'] or 0

    return render_template('food_wastage.html', records=records, weekly=weekly,
                           today_total=today_total, role=session.get('role'))


@bp.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    if session.get('role') != 'warden':
        flash('Only wardens can log food wastage.', 'warning')
        return redirect(url_for('food.view'))

    if request.method == 'POST':
        meal_type   = request.form.get('meal_type')
        quantity_kg = request.form.get('quantity_kg')
        log_date    = request.form.get('date') or str(date.today())
        notes       = request.form.get('notes', '').strip()
        uid         = session['user_id']

        if not meal_type or not quantity_kg:
            flash('Please fill in all required fields.', 'danger')
            return render_template('food_form.html')

        cursor = get_cursor()
        cursor.execute(
            "INSERT INTO food_wastage (meal_type, quantity_kg, date, notes, logged_by) VALUES (?, ?, ?, ?, ?)",
            (meal_type, float(quantity_kg), log_date, notes, uid)
        )
        commit_db()
        flash('Food wastage logged successfully!', 'success')
        return redirect(url_for('food.view'))

    return render_template('food_form.html', today=date.today())
