from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import User, Movie, Message

from datetime import datetime, timezone


@app.route('/graphics')
def graphics():
    return render_template('graphics.html')

@app.route('/iphonephotos')
def iphonephotos():
    return render_template('iphonephotos.html')


@app.route('/cameraphotos')
def cameraphotos():
    return render_template('cameraphotos.html')


@app.route('/filmphotos')
def filmphotos():
    return render_template('filmphotos.html')


@app.route('/industrial')
def industrial():
    return render_template('industrial.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))

        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))

        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))

    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))

        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


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
        return redirect(url_for('index'))

    return render_template('settings.html')


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
@app.route('/message/delete/<int:message_id>', methods=['POST'])
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
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))