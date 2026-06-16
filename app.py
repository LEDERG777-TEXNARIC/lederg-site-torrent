import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Game
from io import BytesIO

app = Flask(__name__)
app.config['f7a8b3c9d1e2f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----- Вспомогательные функции -----
def create_admin_if_not_exists():
    """Создаёт админа, если его нет (логин и пароль из переменных окружения)."""
    admin_username = os.environ.get('LEDERG', 'admin')
    admin_password = os.environ.get('LEDERG648562)', 'admin123')
    user = User.query.filter_by(username=admin_username).first()
    if not user:
        hashed = generate_password_hash(admin_password)
        admin = User(username=admin_username, password_hash=hashed, is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print(f'Создан администратор: {admin_username}')

# ----- Маршруты -----
@app.route('/')
def index():
    games = Game.query.order_by(Game.created_at.desc()).all()
    return render_template('index.html', games=games)

@app.route('/game/<int:game_id>')
def game_page(game_id):
    game = Game.query.get_or_404(game_id)
    return render_template('game.html', game=game)

@app.route('/download/<int:game_id>')
def download_torrent(game_id):
    game = Game.query.get_or_404(game_id)
    if not game.torrent_data:
        abort(404)
    return send_file(
        BytesIO(game.torrent_data),
        as_attachment=True,
        download_name=game.torrent_filename or f'{game.title}.torrent'
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Пользователь уже существует.', 'danger')
            return redirect(url_for('register'))
        hashed = generate_password_hash(password)
        user = User(username=username, password_hash=hashed, is_admin=False)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна! Войдите.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вы вошли.', 'success')
            return redirect(url_for('index'))
        flash('Неверные логин или пароль.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли.', 'success')
    return redirect(url_for('index'))

# ----- Админ-панель -----
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        year = request.form['year']
        image_url = request.form['image_url']
        torrent_file = request.files['torrent_file']
        if torrent_file and torrent_file.filename.endswith('.torrent'):
            torrent_data = torrent_file.read()
            torrent_filename = torrent_file.filename
        else:
            flash('Пожалуйста, загрузите файл с расширением .torrent', 'danger')
            return redirect(url_for('admin'))
        game = Game(
            title=title,
            description=description,
            category=category,
            year=year,
            image_url=image_url,
            torrent_data=torrent_data,
            torrent_filename=torrent_filename
        )
        db.session.add(game)
        db.session.commit()
        flash('Игра добавлена!', 'success')
        return redirect(url_for('admin'))
    return render_template('admin.html')

# ----- Создание таблиц и админа при старте -----
with app.app_context():
    db.create_all()
    create_admin_if_not_exists()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
