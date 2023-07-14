from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    response = requests.get('https://api.themoviedb.org/3/movie/popular?api_key=YOUR_API_KEY')
    movies = response.json()['results']  # TMDB API returns the movie list under 'results' key
    base_url = 'https://image.tmdb.org/t/p/w500'

    for movie in movies:
        movie['poster_path'] = base_url + movie['poster_path']

    return render_template('home.html', movies=movies)





