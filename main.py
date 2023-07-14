import random
import requests
import sqlite3
from watchlist import view_watchlist, remove_from_watchlist

def create_table():
    conn = sqlite3.connect('watchlist.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movies
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT,
                 overview TEXT,
                 rating REAL,
                 platforms TEXT,
                 image_url TEXT)''')
    conn.commit()
    conn.close()

def add_movie_to_watchlist(movie_info):
    conn = sqlite3.connect('watchlist.db')
    c = conn.cursor()
    c.execute('''INSERT INTO movies (title, overview, rating, platforms, image_url)
                 VALUES (?, ?, ?, ?, ?)''',
              (movie_info['Title'], movie_info['Overview'], movie_info['Rating'],
               ', '.join(movie_info['Streaming Platforms']), movie_info['Image URL']))
    conn.commit()
    conn.close()

def search_movie(api_key, movie_title):
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}'
    response = requests.get(url)
    data = response.json()

    if 'results' in data:
        results = data['results']
        if results:
            movie_id = results[0]['id']
            return get_movie_details(api_key, movie_id)
    return None


def get_movie_details(api_key, movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()

    title = data.get('title')
    overview = data.get('overview')
    rating = data.get('vote_average')
    platforms = get_movie_platforms(api_key, movie_id)
    image_url = f"https://image.tmdb.org/t/p/w500/{data.get('poster_path')}"

    return {
        'Title': title,
        'Overview': overview,
        'Rating': rating,
        'Streaming Platforms': platforms,
        'Image URL': image_url
    }


def get_movie_platforms(api_key, movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}'
    response = requests.get(url)
    data = response.json()

    if 'results' in data and 'US' in data['results']:
        providers = data['results']['US'].get('flatrate')
        if providers:
            platform_names = [provider['provider_name'] for provider in providers]
            return platform_names
            
    return 'Streaming information not available.'


def recommend_movies(api_key, user_platforms, genre):
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&with_genres={genre}'
    response = requests.get(url)
    data = response.json()

    if 'results' in data:
        movies = data['results']
        random.shuffle(movies)
        for movie in movies:
            movie_id = movie['id']
            movie_info = get_movie_details(api_key, movie_id)
            if movie_info:
                platforms = movie_info['Streaming Platforms']
                if any(platform in user_platforms for platform in platforms):
                    return movie_info
    return None


def login():
    while True:
        choice = input("Choose an option:\n1. Existing User (Login)\n2. New User (Create Account)\n3. Exit\n")
        if choice == '1':
            existing_username = input('Enter your username: ')
            existing_password = input('Enter your password: ')

            # Replace with your existing user authentication logic
            if authenticate_user(existing_username, existing_password):
                print('Login successful!')
                return True
            else:
                print('Invalid username or password. Please try again.')
        elif choice == '2':
            new_username = input('Enter a new username: ')
            new_password = input('Enter a new password: ')

            if create_user(new_username, new_password):
                print('Account created successfully!')
                return True
            else:
                print('Failed to create an account. Please try again.')
        elif choice == '3':
            print('Exiting...')
            return False
        else:
            print('Invalid choice. Please try again.')


def create_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Create the users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY,
                 password TEXT)''')

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error:
        conn.rollback()
        conn.close()
        return False


def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()

    if result is not None:
        return True
    else:
        return False
    

def main():
    if not login():
        return

    while True:
        choice = input("Choose an option:\n1. Search Movie by Title\n2. Search Movie by Genre and Streaming Platforms\n"
                       "3. View Watchlist\n4. Log off\n")

        if choice == '1':
            api_key = '9dcbbdc0af2f471264786a8eebb6b1e3'
            movie_title = input('Enter a movie title: ')

            create_table()
            
            movie_info = search_movie(api_key, movie_title)
            if movie_info:
                print('Title:', movie_info['Title'])
                print('Overview:', movie_info['Overview'])
                print('Rating:', movie_info['Rating'])
                platforms = movie_info['Streaming Platforms']
                if platforms == 'Streaming information not available.':
                    print('Streaming Platforms: Not available')
                else:
                    print('Streaming Platforms:', ', '.join(platforms))
                print('Image:', movie_info['Image URL'])
                add_movie = input("Do you want to add this movie to your Watchlist? (yes or no) ")
                if add_movie.lower().strip() == "yes":
                    add_movie_to_watchlist(movie_info)
                    print('Movie added to watchlist!')
                else:
                    print('Movie was not added to watchlist.')
            else:
                print('No movie found with that title.')

        elif choice == '2':
            search_by_genre_and_platform()

        elif choice == '3':
            view_watchlist()
            choice = input("Choose an option:\n1. Go back to main menu\n2. Remove movie from Watchlist\n")
            if choice == '1':
                # do nothing
                print("Back to Main Menu")
            elif choice == '2':
                remove_from_watchlist()
            else:
                print("Invalid choice. Please try again.")

        elif choice == '4':
            print('Logging off...')
            break

        else:
            print("Invalid choice. Please try again.")


def search_by_genre_and_platform():
    api_key = '9dcbbdc0af2f471264786a8eebb6b1e3'
    user_platforms = input("What streaming platforms do you have? ")
    genre = input("What movie genre are you interested in? ")

    regenerate_movie = True
    while regenerate_movie:
        movie_info = recommend_movies(api_key, user_platforms, genre)
        if movie_info:
            print("Recommended Movie:")
            print('Title:', movie_info['Title'])
            print('Overview:', movie_info['Overview'])
            print('Rating:', movie_info['Rating'])
            print('Streaming Platforms:', ', '.join(movie_info['Streaming Platforms']))
            print('Image:', movie_info['Image URL'])

            add_to_watchlist = input("Do you want to add this movie to your watchlist? (yes or no) ")
            if add_to_watchlist.lower().strip() == "yes":
                add_movie_to_watchlist(movie_info)
                print('Movie added to watchlist!')
            regenerate_movie = False
            break

        new_movie = input("Do you want another movie option? (yes or no) ")
        if new_movie.lower().strip() == "no":
            print("No movies added to watchlist.")
            regenerate_movie = False
            break
        else:
            print("No recommended movies found for your streaming platform.")
            new_movie = input("Do you want to input different streaming platforms? (yes or no) ")
            if new_movie.lower().strip() == "no":
                print("No recommended movies found.")
                regenerate_movie = False
                break
            else:
                user_platforms = input("What streaming platforms do you have? ")
                genre = input("What movie genre are you interested in? ")


if __name__ == '__main__':
    main()

#for demo, use toy story and barbie for option 1
#use netlix --> action for option 2