from flask import render_template, request, url_for, redirect, flash, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user

from PersonalWebsite import app, db
from PersonalWebsite.models import User, Movie, Message

from datetime import datetime, timezone


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])

@app.route('/')
def index():
    return render_template('index.html')

# create message
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'POST':
        name = request.form.get('name')
        content = request.form.get('content')
        time = datetime.now(timezone.utc)
        if not name or not content or len(name) > 60:
            flash('Hey? One more time!')
            return redirect(url_for('messages'))
        message = Message(name=name, content=content, time=time)
        db.session.add(message)
        db.session.commit()
        flash('Thank you :)')
        return redirect(url_for('messages'))

    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示的消息数量，可以根据需要调整
    pagination = Message.query.order_by(Message.time.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    messages = pagination.items

    return render_template('messages.html', messages=messages, pagination=pagination)


# editting message is not allowed 

# delete message
@app.route('/messages/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted.')
    return redirect(url_for('messages'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()

        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('messages'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        user = User.query.first()
        user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('messages'))

    return render_template('settings.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('messages'))


@app.route('/_next/<path:filename>')
def serve_next(filename):
    return send_from_directory('static/_next', filename, as_attachment=False)

@app.route('/index.html')
def serve_react_index():
    return send_from_directory('static', 'index.html')