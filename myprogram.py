import tkinter as tk
from tkinter import messagebox
import mysql.connector
import random

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="test"
)

cursor = db.cursor()

def register():
    username = reg_username.get()
    password = reg_password.get()

    # Check if username already exists
    cursor.execute("SELECT * FROM UserAccounts WHERE username = %s", (username,))
    if cursor.fetchone() is not None:
        messagebox.showerror("Error", "Username already exists.")
        return

    # Insert new user into database
    cursor.execute("INSERT INTO UserAccounts (username, password) VALUES (%s, %s)", (username, password))
    db.commit()
    messagebox.showinfo("Success", "Registration successful.")

def login():
    username = login_username.get()
    password = login_password.get()

    # Check if username and password match
    cursor.execute("SELECT * FROM UserAccounts WHERE username = %s AND password = %s", (username, password))
    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Invalid username or password.")
    else:
        messagebox.showinfo("Success", "Login successful.")
        show_main_page()

def show_main_page():
    login_frame.pack_forget()

    # Create main page
    main_page = tk.Frame(root)
    main_page.pack(padx=20, pady=20)

    # Main Page Buttons
    search_button = tk.Button(main_page, text="Search", command=search)
    search_button.grid(row=0, column=0, padx=10, pady=10)

    add_movie_button = tk.Button(main_page, text="Add Movie", command=add_movie)
    add_movie_button.grid(row=0, column=1, padx=10, pady=10)

    movie_quiz_button = tk.Button(main_page, text="Movies Quiz", command=movie_quiz)
    movie_quiz_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

def search():
    def search_movie():
        title = search_entry.get()
        cursor.execute("SELECT movie_id, title FROM Movies WHERE title LIKE %s", ('%' + title + '%',))
        movies = cursor.fetchall()
        if not movies:
            messagebox.showinfo("Info", "No movies found with the given title.")
            return

        search_results_window = tk.Toplevel(root)
        search_results_window.title("Search Results")

        selected_movie_id = tk.StringVar()

        search_results_listbox = tk.Listbox(search_results_window)
        search_results_listbox.pack(fill=tk.BOTH, expand=True)

        # Populate listbox with search results
        for movie_id, movie_title in movies:
            search_results_listbox.insert(tk.END, f"{movie_title} (ID: {movie_id})")

        def show_movie_details():
            selected_index = search_results_listbox.curselection()
            if not selected_index:
                messagebox.showinfo("Info", "Please select a movie.")
                return

            selected_movie = search_results_listbox.get(selected_index)
            selected_movie_id = selected_movie.split("(ID: ")[1][:-1]

            display_movie_details(selected_movie_id)

        select_button = tk.Button(search_results_window, text="Select Movie", command=show_movie_details)
        select_button.pack()

    def display_movie_details(movie_id):
        movie_details_window = tk.Toplevel(root)
        movie_details_window.title("Movie Details")

        # Retrieve movie details
        cursor.execute("SELECT * FROM Movies WHERE movie_id = %s", (movie_id,))
        movie_details = cursor.fetchone()

        # Display movie details
        movie_details_label = tk.Label(movie_details_window, text=f"Title: {movie_details[1]}\nRelease Date: {movie_details[2]}\nGenre: {movie_details[3]}")
        movie_details_label.pack()

        # Get director name
        cursor.execute("SELECT name FROM Directors WHERE director_id = %s", (movie_details[4],))
        director_name = cursor.fetchone()[0]
        director_label = tk.Label(movie_details_window, text=f"Director: {director_name}")
        director_label.pack()

        # Get actors
        cursor.execute("SELECT name FROM Actors INNER JOIN Movie_Actors ON Actors.actor_id = Movie_Actors.actor_id WHERE Movie_Actors.movie_id = %s", (movie_id,))
        actors = cursor.fetchall()
        actors_label = tk.Label(movie_details_window, text="Actors: " + ", ".join(actor[0] for actor in actors))
        actors_label.pack()

        # Get existing reviews
        cursor.execute("SELECT review_text FROM Reviews WHERE movie_id = %s", (movie_id,))
        reviews = cursor.fetchall()
        reviews_label = tk.Label(movie_details_window, text="Reviews:")
        reviews_label.pack()
        for review in reviews:
            review_text = review[0]
            review_text_label = tk.Label(movie_details_window, text=review_text)
            review_text_label.pack()

        # Get average rating
        cursor.execute("SELECT AVG(rating) FROM Ratings WHERE movie_id = %s", (movie_id,))
        avg_rating = cursor.fetchone()[0]
        avg_rating_label = tk.Label(movie_details_window, text=f"Average Rating: {avg_rating:.1f}")
        avg_rating_label.pack()

        # Add Review and Rating
        review_frame = tk.Frame(movie_details_window)
        review_frame.pack(pady=10)
        new_review_label = tk.Label(review_frame, text="Add Your Review:")
        new_review_label.grid(row=0, column=0, sticky="w")
        new_review_entry = tk.Entry(review_frame, width=50)
        new_review_entry.grid(row=0, column=1, padx=5)

        rating_label = tk.Label(review_frame, text="Rating (out of 10):")
        rating_label.grid(row=1, column=0, sticky="w")
        rating_scale = tk.Scale(review_frame, from_=0, to=10, orient=tk.HORIZONTAL)
        rating_scale.grid(row=1, column=1)

        add_review_button = tk.Button(review_frame, text="Add Review and Rating", command=lambda: add_review_and_rating(movie_id, new_review_entry.get(), rating_scale.get()))
        add_review_button.grid(row=2, column=0, columnspan=2, pady=5)

    def add_review_and_rating(movie_id, review_text, rating):
        if not review_text:
            messagebox.showinfo("Info", "Please enter a review.")
            return

        cursor.execute("INSERT INTO Reviews (movie_id, review_text) VALUES (%s, %s)", (movie_id, review_text))
        db.commit()

        cursor.execute("INSERT INTO Ratings (movie_id, rating) VALUES (%s, %s)", (movie_id, rating))
        db.commit()

        messagebox.showinfo("Info", "Review and Rating added successfully.")
        display_movie_details(movie_id)  # Refresh the movie details window to display the new review and rating

    # Create main window
    root = tk.Tk()
    root.title("Movie Database Application")

    # Search Frame
    search_frame = tk.Frame(root)
    search_frame.pack(padx=20, pady=20)

    search_label = tk.Label(search_frame, text="Enter Movie Title:")
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame)
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text="Search", command=search_movie)
    search_button.grid(row=0, column=2)

def add_movie():
    # Functionality for adding a movie page
    add_movie_window = tk.Toplevel(root)
    add_movie_window.title("Add Movie")

    # Labels and Entry Widgets for Movie Details
    title_label = tk.Label(add_movie_window, text="Title:")
    title_label.grid(row=0, column=0, sticky="e")
    title_entry = tk.Entry(add_movie_window)
    title_entry.grid(row=0, column=1)

    release_date_label = tk.Label(add_movie_window, text="Release Date (YYYY-MM-DD):")
    release_date_label.grid(row=1, column=0, sticky="e")
    release_date_entry = tk.Entry(add_movie_window)
    release_date_entry.grid(row=1, column=1)

    genre_label = tk.Label(add_movie_window, text="Genre:")
    genre_label.grid(row=2, column=0, sticky="e")
    genre_entry = tk.Entry(add_movie_window)
    genre_entry.grid(row=2, column=1)

    director_label = tk.Label(add_movie_window, text="Director:")
    director_label.grid(row=3, column=0, sticky="e")
    director_entry = tk.Entry(add_movie_window)
    director_entry.grid(row=3, column=1)

    actors_label = tk.Label(add_movie_window, text="Main Actor")
    actors_label.grid(row=4, column=0, sticky="e")
    actors_entry = tk.Entry(add_movie_window)
    actors_entry.grid(row=4, column=1)

    # Function to add movie to the database
    def add_movie_to_database():
        # Extract data from entry widgets
        title = title_entry.get()
        release_date = release_date_entry.get()
        genre = genre_entry.get()
        director = director_entry.get()
        actors = actors_entry.get().split(",")

        # Insert director into Directors table if not exists
        cursor.execute("SELECT director_id FROM Directors WHERE name = %s", (director,))
        director_id = cursor.fetchone()
        if not director_id:
            cursor.execute("INSERT INTO Directors (name) VALUES (%s)", (director,))
            db.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            director_id = cursor.fetchone()[0]
        else:
            director_id = director_id[0]

        # Insert actors into Actors table if not exists
        actor_ids = []
        for actor in actors:
            cursor.execute("SELECT actor_id FROM Actors WHERE name = %s", (actor,))
            actor_id = cursor.fetchone()
            if not actor_id:
                cursor.execute("INSERT INTO Actors (name) VALUES (%s)", (actor,))
                db.commit()
                cursor.execute("SELECT LAST_INSERT_ID()")
                actor_id = cursor.fetchone()[0]
            else:
                actor_id = actor_id[0]
            actor_ids.append(actor_id)

        # Insert movie into Movies table
        cursor.execute("INSERT INTO Movies (title, release_date, genre, director_id) VALUES (%s, %s, %s, %s)", (title, release_date, genre, director_id))
        db.commit()
        cursor.execute("SELECT LAST_INSERT_ID()")
        movie_id = cursor.fetchone()[0]

        # Insert actors and movie associations into Movie_Actors table
        for actor_id in actor_ids:
            cursor.execute("INSERT INTO Movie_Actors (movie_id, actor_id) VALUES (%s, %s)", (movie_id, actor_id))
            db.commit()

        messagebox.showinfo("Info", "Movie added successfully.")

    # Button to add movie to the database
    add_button = tk.Button(add_movie_window, text="Add Movie", command=add_movie_to_database)
    add_button.grid(row=5, columnspan=2, pady=10)


def movie_quiz():
    # Functionality for movie quiz page
    movie_quiz_window = tk.Toplevel(root)
    movie_quiz_window.title("Movie Quiz")

    # Define a list of possible question types
    question_types = ["actor_birth_year", "actor_nationality", "movie_release_year", "movie_genre", "director"]

    # Select a random question type
    question_type = random.choice(question_types)

    # Generate and display the question
    question_label = tk.Label(movie_quiz_window, text="Question:")
    question_label.pack()

    if question_type == "actor_birth_year":
        # Select a random actor from the database
        cursor.execute("SELECT name, dob FROM Actors")
        actor_info = cursor.fetchall()
        actor = random.choice(actor_info)
        actor_name, actor_dob = actor

        # Generate the question and answer
        question_text = f"What year was {actor_name} born on?"
        correct_answer = str(actor_dob.year)

    elif question_type == "actor_nationality":
        # Select a random actor and their nationality from the database
        cursor.execute("SELECT name, nationality FROM Actors")
        actor_info = cursor.fetchall()
        actor = random.choice(actor_info)
        actor_name, actor_nationality = actor

        # Generate the question and answer
        question_text = f"What is the nationality of {actor_name}?"
        correct_answer = actor_nationality

    elif question_type == "movie_release_year":
        # Select a random movie from the database
        cursor.execute("SELECT title, release_date FROM Movies")
        movie_info = cursor.fetchall()
        movie = random.choice(movie_info)
        movie_title, movie_release_date = movie

        # Generate the question and answer
        question_text = f"What year did the movie '{movie_title}' release?"
        correct_answer = str(movie_release_date.year)

    elif question_type == "movie_genre":
        # Select a random movie and its genre from the database
        cursor.execute("SELECT title, genre FROM Movies")
        movie_info = cursor.fetchall()
        movie = random.choice(movie_info)
        movie_title, movie_genre = movie

        # Generate the question and answer
        question_text = f"What is the genre of the movie '{movie_title}'?"
        correct_answer = movie_genre

    elif question_type == "director":
        # Select a random movie and its director from the database
        cursor.execute("SELECT Movies.title, Directors.name FROM Movies INNER JOIN Directors ON Movies.director_id = Directors.director_id")
        movie_director_info = cursor.fetchall()
        movie_director = random.choice(movie_director_info)
        movie_title, director_name = movie_director

        # Generate the question and answer
        question_text = f"Who directed the movie '{movie_title}'?"
        correct_answer = director_name

    # Display the question
    question_label = tk.Label(movie_quiz_window, text=question_text)
    question_label.pack()

    # Entry widget for user's answer
    answer_entry = tk.Entry(movie_quiz_window)
    answer_entry.pack()

    # Function to check the user's answer
    def check_answer():
        user_answer = answer_entry.get()

        if user_answer.lower() == correct_answer.lower():
            messagebox.showinfo("Correct", "Your answer is correct!")
        else:
            messagebox.showinfo("Incorrect", f"Sorry, the correct answer is: {correct_answer}")

    # Button to check the answer
    check_button = tk.Button(movie_quiz_window, text="Check Answer", command=check_answer)
    check_button.pack()

# Create main window
root = tk.Tk()
root.title("Movie Database Application")

# Register/Login Frame
login_frame = tk.Frame(root)
login_frame.pack(padx=20, pady=20)

# Register
reg_username_label = tk.Label(login_frame, text="Username:")
reg_username_label.grid(row=0, column=0, sticky="e")
reg_username = tk.Entry(login_frame)
reg_username.grid(row=0, column=1)

reg_password_label = tk.Label(login_frame, text="Password:")
reg_password_label.grid(row=1, column=0, sticky="e")
reg_password = tk.Entry(login_frame, show="*")
reg_password.grid(row=1, column=1)

register_button = tk.Button(login_frame, text="Register", command=register)
register_button.grid(row=2, column=0, columnspan=2, pady=5)

# Login
login_username_label = tk.Label(login_frame, text="Username:")
login_username_label.grid(row=3, column=0, sticky="e")
login_username = tk.Entry(login_frame)
login_username.grid(row=3, column=1)

login_password_label = tk.Label(login_frame, text="Password:")
login_password_label.grid(row=4, column=0, sticky="e")
login_password = tk.Entry(login_frame, show="*")
login_password.grid(row=4, column=1)

login_button = tk.Button(login_frame, text="Login", command=login)
login_button.grid(row=5, column=0, columnspan=2, pady=5)

root.mainloop()
