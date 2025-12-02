import os
import sqlite3
from flask import Flask

# Twój import do rating_diff (zostaje)
from rating_diff import update_user_rating

# Importujemy funkcje z plików (patrz niżej)
from routes.home_route import home
from routes.history_route import history
from routes.puzzle_route import puzzle
from routes.result_route import submit_result

app = Flask(__name__)

# Podpinamy dokładnie te same funkcje do adresów URL:
app.route('/')(home)
app.route('/history')(history)
app.route('/puzzle', methods=['GET','POST'])(puzzle)
app.route('/submit_result', methods=['POST'])(submit_result)

if __name__ == '__main__':
    app.run(debug=True)
