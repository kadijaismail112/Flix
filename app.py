from flask import Flask, render_template, request
from main import add_movie_to_watchlist, search_movie, create_table
import requests
import sqlite3
import json


app = Flask(__name__)

@app.route('/')
def home():
    # url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}'
    response = requests.get('https://api.themoviedb.org/3/movie/popular?api_key=9dcbbdc0af2f471264786a8eebb6b1e3')
    movies = response.json()['results']  # TMDB API returns the movie list under 'results' key
    base_url = 'https://image.tmdb.org/t/p/w500'
    # print(response)
    # print(movies)
    for movie in movies:
        movie['poster_path'] = base_url + movie['poster_path']
    print(movies)
    return render_template('index.html', movies=movies)

@app.route('/add-list', methods=['POST'])
def add_list():
    movie = request.form.get('movie')
    data = search_movie("9dcbbdc0af2f471264786a8eebb6b1e3", movie)
    add_movie_to_watchlist(data)
    return 'success'

@app.route("/create-tables")
def create_tables():
    create_table()
    return 'success'

@app.route('/watchlist')
def watchlist():
    conn = sqlite3.connect('watchlist.db')
    conn.row_factory = sqlite3.Row  # use sqlite3.Row to access columns by name
    c = conn.cursor()
    c.execute("SELECT * FROM movies")
    movies = [dict(row) for row in c.fetchall()]  # convert each row to a dictionary
    conn.close()
    print(movies)
    return render_template('watchlist.html', movies=movies)

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/delete-tables')
def delete_tables():
    conn = sqlite3.connect('watchlist.db')
    c = conn.cursor()
    c.execute("DROP TABLE movies")
    conn.commit()
    conn.close()
    return 'success'

if __name__ == '__main__':
    app.run(debug=True)
