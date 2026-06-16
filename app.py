import os
import json
from flask import Flask, render_template, abort

app = Flask(__name__)

# Путь к папке с JSON-файлами
GAMES_DIR = os.path.join(os.path.dirname(__file__), 'games')

def load_all_games():
    """Загружает все JSON-файлы из папки games/ и возвращает список словарей."""
    games = []
    if not os.path.exists(GAMES_DIR):
        return games
    for filename in os.listdir(GAMES_DIR):
        if filename.endswith('.json'):
            path = os.path.join(GAMES_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    game = json.load(f)
                    games.append(game)
                except Exception as e:
                    print(f"Ошибка чтения {filename}: {e}")
    return games

@app.route('/')
def index():
    games = load_all_games()
    return render_template('index.html', games=games)

@app.route('/game/<game_id>')
def game_page(game_id):
    games = load_all_games()
    # Ищем игру по id
    for game in games:
        if game.get('id') == game_id:
            return render_template('game.html', game=game)
    abort(404)  # Если не найдено

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
