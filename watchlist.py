import sqlite3

# To use in main.py make sure to do “from watchlist import view_watchlist, remove_from_watchlist”

def view_watchlist():
    conn = sqlite3.connect('watchlist.db')
    c = conn.cursor()

    c.execute("SELECT * FROM movies")
    movies = c.fetchall()
    if movies:
        print("Watchlist Movies:")
        for movie in movies:
            print('Title:', movie[1])
            print('Overview:', movie[2])
            print('Rating:', movie[3])
            print('Streaming Platforms:', movie[4])
            print("--------------------")
    else:
        print("Watchlist is empty.")

    conn.close()

def remove_from_watchlist():
    movie_id = input("Which movie would you like to remove from the watchlist (Input the Movie ID)?")
    conn = sqlite3.connect('watchlist.db')
    c = conn.cursor()

    while True:
        c.execute("SELECT * FROM movies WHERE id=?", (movie_id,))
        movie = c.fetchone()

        if movie:
            c.execute("DELETE FROM movies WHERE id=?", (movie_id,))
            conn.commit()
            print("Movie removed successfully!")
            break
        else:
            print("Invalid Movie ID. Movie not found in the watchlist.")
            new_choice = input("Would you like to input a new movie ID? (yes or no)")
            if new_choice.lower().strip() == "no":
                print("No movie removed.")
                break
            else:
                movie_id = input("Which movie would you like to remove from the watchlist (Input the Movie ID)?")

    conn.close()