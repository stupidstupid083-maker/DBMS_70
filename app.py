from flask import Flask, render_template, session, redirect, url_for
from config import Config
from services.db import close_db
from routes import auth, student, warden, attendance, complaint, leave, food, notification, menu, roommate, emergency, onboarding
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)


# Custom Jinja2 filter: handles both datetime objects and SQLite string dates
@app.template_filter('datefmt')
def datefmt_filter(value, fmt='%d %b %Y'):
    if value is None:
        return '-'
    if isinstance(value, str):
        # Try common SQLite timestamp formats
        for parse_fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
            try:
                return datetime.strptime(value, parse_fmt).strftime(fmt)
            except ValueError:
                continue
        return value  # Return raw string if parsing fails
    try:
        return value.strftime(fmt)
    except Exception:
        return str(value)


@app.template_filter('datetimefmt')
def datetimefmt_filter(value, fmt='%d %b %Y, %I:%M %p'):
    return datefmt_filter(value, fmt)

# Register all blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(student.bp)
app.register_blueprint(warden.bp)
app.register_blueprint(complaint.bp)
app.register_blueprint(attendance.bp)
app.register_blueprint(leave.bp)
app.register_blueprint(food.bp)
app.register_blueprint(notification.bp)
app.register_blueprint(menu.bp)
app.register_blueprint(roommate.bp)
app.register_blueprint(emergency.bp)
app.register_blueprint(onboarding.bp)

# Run safe DB column migrations (adds onboarding_complete & allergies if missing)
with app.app_context():
    onboarding.run_migrations()

app.teardown_appcontext(close_db)


@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'warden':
            return redirect(url_for('warden.dashboard'))
        return redirect(url_for('student.dashboard'))
    return render_template('index.html')


@app.context_processor
def inject_unread_count():
    if 'user_id' in session:
        from services.db import get_cursor
        uid = session['user_id']
        try:
            cursor = get_cursor()
            cursor.execute("""
                SELECT COUNT(*) AS cnt FROM notifications
                WHERE (user_id = ? OR user_id IS NULL) AND is_read = 0
            """, (uid,))
            result = cursor.fetchone()
            return {'unread_count': result['cnt'] if result else 0}
        except Exception:
            return {'unread_count': 0}
    return {'unread_count': 0}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
