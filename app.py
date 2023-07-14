from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    response = requests.get('https://api.themoviedb.org/3/movie/popular?api_key=9dcbbdc0af2f471264786a8eebb6b1e3')
    movies = response.json()['results']  # TMDB API returns the movie list under 'results' key
    base_url = 'https://image.tmdb.org/t/p/w500'
    # print(response)
    # print(movies)
    for movie in movies:
        movie['poster_path'] = base_url + movie['poster_path']
    print(movies)
    return render_template('index.html', movies=movies)

if __name__ == '__main__':
    app.run(debug=True)