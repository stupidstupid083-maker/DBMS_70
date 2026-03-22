from flask import Blueprint, request, session, redirect, url_for, render_template, flash
from werkzeug.security import check_password_hash, generate_password_hash
from services.db import get_cursor, commit_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role     = request.form.get('role', 'student')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html', role=role)

        cursor = get_cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = ?", (username, role))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id']   = user['id']
            session['username']  = user['username']
            session['full_name'] = user['full_name']
            session['role']      = user['role']
            flash(f"Welcome back, {user['full_name']}!", 'success')
            if role == 'warden':
                return redirect(url_for('warden.dashboard'))
            else:
                # Check if onboarding is complete for student
                onboarding_done = user['onboarding_complete'] if 'onboarding_complete' in user.keys() else 1
                if not onboarding_done:
                    return redirect(url_for('onboarding.step1'))
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid credentials. Please check your username and password.', 'danger')

    return render_template('login.html', role=request.args.get('role', 'student'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username    = request.form.get('username', '').strip()
        password    = request.form.get('password', '')
        full_name   = request.form.get('full_name', '').strip()
        email       = request.form.get('email', '').strip()
        role        = request.form.get('role', 'student')
        roll_number = request.form.get('roll_number', '').strip()
        course      = request.form.get('course', '').strip()
        room_number = request.form.get('room_number', '').strip()
        phone       = request.form.get('phone', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        department  = request.form.get('department', '').strip()

        if not all([username, password, full_name, email]):
            flash('All required fields must be filled.', 'danger')
            return render_template('register.html')

        hashed_pw = generate_password_hash(password)
        cursor = get_cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password, full_name, email, role) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_pw, full_name, email, role)
            )
            user_id = cursor.lastrowid

            if role == 'student':
                cursor.execute(
                    "INSERT INTO students (user_id, roll_number, course, room_number, phone) VALUES (?, ?, ?, ?, ?)",
                    (user_id, roll_number or f'ROLL{user_id:04d}', course, room_number, phone)
                )
            else:
                cursor.execute(
                    "INSERT INTO warden (user_id, employee_id, department, phone) VALUES (?, ?, ?, ?)",
                    (user_id, employee_id or f'EMP{user_id:04d}', department, phone)
                )

            commit_db()

            if role == 'student':
                # Auto-login and redirect to the 3-step onboarding wizard
                session['user_id']   = user_id
                session['username']  = username
                session['full_name'] = full_name
                session['role']      = 'student'
                flash(f"Welcome, {full_name}! Let's set up your hostel profile.", 'success')
                return redirect(url_for('onboarding.step1'))
            else:
                flash('Warden account created successfully! You can now log in.', 'success')
                return redirect(url_for('auth.login'))

        except Exception as e:
            flash('Error creating account: Username or email already exists.', 'danger')

    return render_template('register.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
