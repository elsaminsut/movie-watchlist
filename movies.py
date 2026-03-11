from dotenv import load_dotenv
import matplotlib.pyplot as plt
from movie_storage import movie_storage_sql as storage
import os
import random
import requests
import statistics

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_URL = f"http://www.omdbapi.com/?apikey={API_KEY}&t="

def exit_menu():
    """Terminates the loop after printing a message."""
    print("Bye!")
    return True


def get_valid_title(movies, is_new_entry):
    """Asks for a movie title and checks if it's new to the database before returning."""
    while True:
        title = input("Enter movie name: ")
        if len(title) == 0:
            print("Please enter a movie name")
            continue
        if not is_new_entry:
            if title not in movies:
                print(f"Movie '{title}' doesn't exist!")
                continue
            return title
        if title in movies:
            print(f"Movie '{title}' already exists!")
            continue
        return title


def get_valid_rating(allow_blank_input=False, rating_type="new", comment=False):
    """Asks for a movie rating and validates it before returning. Can accept empty inputs if
    allow_blank_input parameter is set to True."""
    while True:
        input_comment = " (leave blank for no minimum rating)" if comment else ""
        raw_input = input(f"Enter {rating_type} movie rating (0-10){input_comment}: ")
        if allow_blank_input and raw_input == "":
            return ""
        try:
            rating = float(raw_input)
            if 0 <= rating <= 10:
                return rating
            print("Invalid rating, please try again")
        except ValueError:
            print("Invalid rating, please try again")


def get_valid_year(allow_blank_input=False, year_type="movie release", comment=False):
    """Asks for a movie release year and validates it before returning.
    A year must be between 1900 and 2030.
    Can accept empty inputs if allow_blank_input parameter is set to True."""
    while True:
        input_comment = " (leave blank for no minimum rating)" if comment else ""
        raw_input = input(f"Enter {year_type} year{input_comment}: ")
        if allow_blank_input and raw_input == "":
            return ""
        try:
            year = int(raw_input)
            if 1900 <= year <= 2030:
                return year
            print("Invalid year, please try again")
        except ValueError:
            print("Invalid year, please try again")


def get_info_from_api(title):
    """Fetch movie information from an external API. Returns movie title, rating, year, and poster URL."""
    url = API_URL + title
    response = requests.get(url)
    movie = response.json()
    if response.ok and movie["Response"] == "True":
        return movie


def list_movies(movies):
    """Fetches all movies in the database and displays a list."""
    print(f"{len(movies)} movies in total")
    for movie, info in movies.items():
        print(f"- {movie} ({info['year']}): {info['rating']}")


def add_movie(movies):
    """Inserts a new movie into the database."""
    search_title = get_valid_title(movies, is_new_entry=True)
    movie = get_info_from_api(search_title)
    if movie:
        rating = movie["Ratings"][0]["Value"].split("/")[0] if movie["Ratings"] else 0 # TODO: handle non existing rating more gracefully
        storage.add_movie(movie["Title"], rating, movie["Year"], movie["Poster"], movie["imdbID"])
        print(f"Movie '{movie["Title"]}' successfully added")
    else:
        print("Movie not found!")


def delete_movie(movies):
    """Deletes a movie from the database."""
    if not movies:
        print("Empty movie database")
    else:
        while True:
            deleted_movie = input("Enter movie name to delete: ")
            if deleted_movie not in movies:
                print(f"Movie '{deleted_movie}' doesn't exist!")
                continue
            storage.delete_movie(deleted_movie)
            print(f"Movie '{deleted_movie}' successfully deleted")
            break


def update_movie(movies):
    """Updates the information of a movie from the database."""
    if not movies:
        print("Empty movie database")
    else:
        update_name = get_valid_title(movies, is_new_entry=False)
        update_rating = get_valid_rating(rating_type="new")
        storage.update_movie(update_name, update_rating)
        print(f"Movie '{update_name}' successfully updated")


def movie_stats(movies):
    """Shows some stats about the movies in the database. Average and median rating, list of
    best and worst movies by rating."""
    if not movies:
        print("Empty movie list")
    else:
        movie_ratings = []
        for movie in list(movies.values()):
            movie_ratings.append(movie["rating"])
        average = round(statistics.mean(movie_ratings), 1)
        median = round(statistics.median(movie_ratings), 1)

        best_movies = []
        worst_movies = []
        best_rating = max(movie_ratings)
        worst_rating = min(movie_ratings)
        for name, info in movies.items():
            if info["rating"] == best_rating:
                best_movies.append(name)
        for name, info in movies.items():
            if info["rating"] == worst_rating:
                worst_movies.append(name)

        print("Average rating:", average)
        print("Median rating:", median)
        print("Best movie(s):", ", ".join(best_movies), best_rating)
        print("Worst movie(s):", ", ".join(worst_movies), worst_rating)


def get_random_movie(movies):
    """Gets a random movie from the database"""
    if not movies:
        print("Empty movie list")
    else:
        rand_movie = random.choice(list(movies.keys()))
        print(f"Your movie for tonight: {rand_movie} ({movies[rand_movie]['year']}), "
              f"it's rated {movies[rand_movie]['rating']}")


def search_movie(movies):
    """Lets the user search for a movie in the database"""
    if not movies:
        print("Empty movie list")
    else:
        search_value = input("Enter part of movie name: ")
        counter = 0
        for name, info in movies.items():
            if search_value.lower() in name.lower():
                print(f"{name} ({info['year']}): {info['rating']}")
                counter += 1
        if counter == 0:
            print(f"Movie {search_value} not found")


def sort_by_rating(movies):
    """Sorts the movies in the database by their ratings and displays the list."""
    if not movies:
        print("Empty movie list")
    else:
        by_rating = lambda x: x[1]["rating"]
        sorted_movies = sorted(list(movies.items()), key=by_rating, reverse=True)
        for movie in sorted_movies:
            print(f"{movie[0]} ({movie[1]['year']}): {movie[1]['rating']}")


def sort_by_year(movies):
    """Sorts the movies in the database by their release year and displays the list.
    The user can choose if the list displays the latest or the oldest movies first."""
    if not movies:
        print("Empty movie list")
    else:
        option_dict = {"Y": True, "N": False}
        while True:
            choice = input("Do you want the latest movies first? (Y/N) ").upper()
            if choice not in option_dict:
                print("Please enter 'Y' or 'N'")
                continue
            latest_first = option_dict[choice]
            by_year = lambda x: x[1]["year"]
            sorted_movies = sorted(list(movies.items()), key=by_year, reverse=latest_first)
            print()
            for movie in sorted_movies:
                print(f"{movie[0]} ({movie[1]['year']}): {movie[1]['rating']}")
            break


def filter_movies(movies):
        """Lets the user filter movies using a minimum rating and a start and end year.
        Blank inputs are considered as empty criteria with no bounds."""
        rating = get_valid_rating(allow_blank_input=True, rating_type="minimum", comment=True)
        min_year = get_valid_year(allow_blank_input=True, year_type="start", comment=True)
        max_year = get_valid_year(allow_blank_input=True, year_type="end", comment=True)

        minimum_rating = rating if rating else 0
        start_year = min_year if min_year else 0
        end_year = max_year if max_year else 3000

        print("\nFiltered movies:")
        counter = 0
        for movie, info in movies.items():
            if info["rating"] > minimum_rating and start_year <= info["year"] <= end_year:
                print(f"{movie} ({info['year']}): {info['rating']} ")
                counter += 1
        if not counter:
            print("No movies found!")


def generate_website(movies):
    """Generates a structured website showcasing a collection of movies.
    This function takes a dictionary of movies and generates an HTML file displaying
    movie posters, titles, ratings, and release years in a grid format. The function
    takes a predefined HTML template and dynamically replaces a placeholder with the
    generated movie HTML content.
    """
    def read_html(filename):
        """Reads from an external HTML file."""
        html_file = open(filename, "r", encoding="utf-8")
        return html_file.read()


    def write_to_file(filename, contents):
        """Writes to an external HTML file."""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(contents)


    def create_movie_card(title, info):
        """Generates an HTML string representing a movie card with a given title and details.
        The card is styled with specific classes to be displayed as a website.
        """
        imdb_url = 'https://www.imdb.com/title/' + info['imdb_id']
        content = ""
        content += '<div>'
        content += '<div class="movie">'
        content += f'<div class="movie-poster"><a href="{imdb_url}" target="_blank"><img src="{info['poster']}" title="{title}"/></a></div>'
        content += f'<div class="movie-info">'
        content += f'<div class="movie-title">{title}</div>'
        content += f'<div class="movie-details">'
        content += f'<div class="movie-rating"><p>⭐</p> <p>{info['rating']}</p></div>'
        content += f'<div class="movie-year">{info['year']}</div>'
        content += '</div>'
        content += '</div>'
        content += '</div>'
        content += '</div>'
        return content


    source_code = read_html("index_template.html")
    output = ""
    for title, info in movies.items():
        output += create_movie_card(title, info)
    source_code_with_movies = source_code.replace("__TEMPLATE_MOVIE_GRID__", output)
    write_to_file("index_movies.html", source_code_with_movies)
    print("Website successfully generated")


def show_histogram(movies):
    """Creates a histogram of movie ratings and saves it into an image file"""
    ratings = []
    for movie in list(movies.values()):
        ratings.append(movie["rating"])
    filename = input("Enter name for your histogram file: ") + ".png"

    fig = plt.figure()
    axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    axes.hist(ratings)
    axes.set_xlabel("Movie ratings")
    axes.set_ylabel("Frequency")
    axes.set_title("Histogram of movie ratings")

    fig.savefig(filename, dpi=200)


def main():
    """Main body of the movie watchlist. Initializes a manu for users to interact with a movie database.
    The user can display the movies in the database and perform CRUD operations on it. There are also
    sorting and filtering options, as well as the possibility of exporting to an HTML file to visualize
    the database in a website.
    """
    choice_dict = {"0": (exit_menu, "Exit"),
    "1": (list_movies, "List movies"),
    "2": (add_movie, "Add movie"),
    "3": (delete_movie, "Delete movie"),
    "4": (update_movie, "Update movie"),
    "5": (movie_stats, "Stats"),
    "6": (get_random_movie, "Random movie"),
    "7": (search_movie, "Search movie"),
    "8": (sort_by_rating, "Movies sorted by rating"),
    "9": (sort_by_year, "Movies sorted by year"),
    "10": (filter_movies, "Filter movies"),
    "11": (generate_website, "Generate website"),
    "12": (show_histogram, "Create rating histogram")
    }

    print("***** My Movies Database *****")

    success = False
    while not success:
        movies = storage.list_movies()
        print()
        for number, function in choice_dict.items():
            print(f"{number}. {function[1]}")
        print()
        choice = input("Enter choice (0-11): ")
        print()
        if choice == "0":
            success = choice_dict[choice][0]()
            continue
        elif choice in choice_dict:
            choice_dict[choice][0](movies)
        else:
            print("Invalid choice")
        print()
        input("Press enter to continue")


if __name__ == "__main__":
    main()