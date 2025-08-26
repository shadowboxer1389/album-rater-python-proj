from tkinter import *
from tkinter import font, ttk
from PIL import ImageTk, Image
import mysql.connector as m
import tkinter as tk

# Database connection
conn = m.connect(host="localhost", user="root", database="album_rater", password="aversion")
cur = conn.cursor()

# --- Database setup ---
def check_database_structure():
    try:
        cur.execute("SHOW TABLES LIKE 'login'")
        if not cur.fetchone():
            cur.execute("""
                CREATE TABLE login (
                    username VARCHAR(255) PRIMARY KEY,
                    password VARCHAR(255) NOT NULL
                )
            """)
            print("Created login table")

        # Only need album_ratings table now
        cur.execute("SHOW TABLES LIKE 'album_ratings'")
        if not cur.fetchone():
            cur.execute("""
                CREATE TABLE album_ratings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255),
                    album_title VARCHAR(255),
                    overall_rating DECIMAL(2,1),
                    rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_album_rating (username, album_title)
                )
            """)
            print("Created album_ratings table")

        conn.commit()
    except Exception as e:
        print(f"Database check error: {e}")

check_database_structure()

# --- Tkinter root ---
root = Tk()
root.geometry("800x500")
root.title("Album Rater")
df = font.Font(family="microsoft jhenghei light", size=70, weight='bold')
df1 = font.Font(family="microsoft jhenghei light", size=20)
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

# Global
current_user = None
album_images = []  # Keep references to album covers

# --- Signup ---
def signup():
    top1 = Toplevel()
    top1.geometry('800x500')
    top1.title("Sign Up")

    Label(top1, text="Create username:", font=df1).pack(padx=10)
    new_user = Entry(top1, font=df1)
    new_user.pack(padx=5)

    Label(top1, text="Create Password:", font=df1).pack(padx=10)
    new_password = Entry(top1, font=df1, show="*")
    new_password.pack()

    status_label = Label(top1, text="", font=df1)
    status_label.pack()

    def handle_signup():
        username = new_user.get().strip()
        password = new_password.get().strip()
        if username and password:
            try:
                qry = "INSERT INTO login VALUES(%s, %s)"
                cur.execute(qry, (username, password))
                conn.commit()
                status_label.config(text="Account created successfully!", fg="green")
                top1.after(2000, top1.destroy)
            except m.IntegrityError:
                status_label.config(text="Username already exists!", fg="red")
            except Exception as e:
                status_label.config(text=f"Error: {e}", fg="red")
        else:
            status_label.config(text="Please fill in both fields", fg="red")

    signup_btn = Button(top1, text="Sign Up", font=df1, command=handle_signup)
    signup_btn.pack(pady=20)

# --- Login ---
def login():
    global current_user
    top2 = Toplevel()
    top2.geometry('800x500')
    top2.title("Login")

    Label(top2, text="Username:", font=df1).pack()
    username_entry = Entry(top2, font=df1)
    username_entry.pack(padx=5)

    Label(top2, text="Password:", font=df1).pack()
    password_entry = Entry(top2, font=df1, show="*")
    password_entry.pack()

    status_label = Label(top2, text="", font=df1)
    status_label.pack()

    def handle_login():
        global current_user
        username1 = username_entry.get().strip()
        password1 = password_entry.get().strip()
        if username1 and password1:
            try:
                qry = "SELECT * FROM login WHERE username=%s AND password=%s"
                cur.execute(qry, (username1, password1))
                r = cur.fetchone()
                if r:
                    current_user = username1
                    status_label.config(text=f"Welcome {username1}!", fg="green")
                    top2.after(2000, top2.destroy)
                else:
                    status_label.config(text="Invalid username or password", fg="red")
            except Exception as e:
                status_label.config(text=f"Database error: {e}", fg="red")
        else:
            status_label.config(text="Please enter both username and password", fg="red")

    login_btn = Button(top2, text="Login", font=df1, command=handle_login)
    login_btn.pack(pady=20)

# --- Profile ---
def profile():
    top = Toplevel()
    top.title("PROFILE")
    top.geometry("800x500")

    if current_user:
        Label(top, text=f"Logged in as: {current_user}", font=df1, fg="green").pack(pady=20)
        Button(top, text="Logout", width=30, font=df1, height=1, bg="red", fg="white",
               command=lambda: [setattr(__builtins__, 'current_user', None), top.destroy()]).pack(pady=10)
    else:
        Label(top, text="Please login or sign up", font=df1).pack(pady=20)
        Button(top, text="Sign Up", width=30, font=df1, height=1, bg="dark slate blue", fg="linen", command=signup).pack(pady=10)
        Button(top, text="Log In", width=30, font=df1, height=1, bg="dark slate blue", fg="linen", command=login).pack(pady=10)

# --- Helpers for album ratings ---
def get_star_display(rating):
    try:
        rating_num = float(rating) if rating else 0.0
        return "★" * int(rating_num) + "☆" * (5 - int(rating_num)) + f" ({rating_num}/5)"
    except:
        return "☆☆☆☆☆ (0/5)"

def get_album_rating(album_title):
    try:
        qry = "SELECT overall_rating FROM album_ratings WHERE username=%s AND album_title=%s"
        cur.execute(qry, (current_user, album_title))
        result = cur.fetchone()
        return float(result[0]) if result else 0.0
    except:
        return 0.0

def save_album_rating(album_title, rating):
    try:
        qry = """INSERT INTO album_ratings (username, album_title, overall_rating) 
                 VALUES (%s, %s, %s)
                 ON DUPLICATE KEY UPDATE overall_rating=%s, rated_at=CURRENT_TIMESTAMP"""
        cur.execute(qry, (current_user, album_title, rating, rating))
        conn.commit()
    except Exception as e:
        print(f"Error saving album rating: {e}")

def open_album_rating_window(album_title, album_name, callback=None):
    rating_window = tk.Toplevel(root)
    rating_window.title(f"Rate Album: {album_name}")
    rating_window.geometry("500x400")
    rating_window.configure(bg='#1a1a2e')

    # Album info
    Label(rating_window, text=f"💿 {album_name}",
          font=('Arial', 16, 'bold'), bg='#1a1a2e', fg='#e94560').pack(pady=20)
    
    Label(rating_window, text="Rate this album overall:",
          font=('Arial', 12), bg='#1a1a2e', fg='white').pack(pady=10)

    current_rating = get_album_rating(album_title)
    rating_var = tk.DoubleVar(value=current_rating)

    # Star rating
    star_frame = tk.Frame(rating_window, bg='#1a1a2e')
    star_frame.pack(pady=20)

    star_buttons = []
    def update_stars(selected):
        rating_var.set(selected)
        for i, btn in enumerate(star_buttons):
            btn.config(text="★" if i < selected else "☆", fg="#ffd700" if i < selected else "#666")

    for i in range(5):
        btn = tk.Button(star_frame, text="☆", font=('Arial', 24),
                        bg='#1a1a2e', fg="#666", bd=0, cursor='hand2',
                        command=lambda r=i+1: update_stars(r))
        btn.pack(side='left', padx=5)
        star_buttons.append(btn)

    update_stars(int(current_rating))

    # Rating label
    rating_label = Label(rating_window, text=f"Current Rating: {current_rating}/5",
                        font=('Arial', 12), bg='#1a1a2e', fg='white')
    rating_label.pack(pady=10)

    def update_rating_label():
        rating_label.config(text=f"Rating: {rating_var.get()}/5")
        rating_window.after(100, update_rating_label)
    
    update_rating_label()

    def save_album_rating_handler():
        new_rating = rating_var.get()
        save_album_rating(album_title, new_rating)
        
        success_label = Label(rating_window, text="✓ Rating saved successfully!",
                             font=('Arial', 12), bg='#1a1a2e', fg='#4CAF50')
        success_label.pack(pady=10)
        
        # If callback provided, call it to refresh the display
        if callback:
            callback()
        
        rating_window.after(2000, rating_window.destroy)

    Button(rating_window, text="Save Album Rating", command=save_album_rating_handler,
           bg='#e94560', fg='white', font=('Arial', 12, 'bold'), 
           cursor='hand2').pack(pady=20)

# --- Main Page ---
def mainpage():
    if not current_user:
        login_prompt = Toplevel()
        login_prompt.title("Login Required")
        login_prompt.geometry("400x200")
        Label(login_prompt, text="Please login to rate albums", font=df1).pack(pady=20)
        Button(login_prompt, text="Login", font=df1, bg="dark slate blue", fg="linen",
               command=lambda: [login(), login_prompt.destroy()]).pack(pady=10)
        return

    top = tk.Toplevel(root)
    top.title("🎵 Music Albums")
    top.geometry("1200x700")
    top.configure(bg='#1a1a2e')

    user_label = tk.Label(top, text=f"👤 Logged in as: {current_user}",
                          font=('Arial', 12, 'bold'),
                          bg='#1a1a2e', fg='#4CAF50')
    user_label.pack(pady=(10, 0))

    title_label = tk.Label(top, text="🎶 Click an Album to Rate It",
                           font=('Arial', 16, 'bold'),
                           bg='#1a1a2e', fg='#e94560')
    title_label.pack(pady=(10, 10))

    image_frame = tk.Frame(top, bg='#1a1a2e')
    image_frame.pack(side='top', pady=20)

    # Album cover paths and setup
    image_info = [
        ("C:/Users/Aarthi V/OneDrive/Desktop/aarthi's_ pics/abc.jpg", "ttpd"),
        ("C:/Users/Aarthi V/OneDrive/Desktop/aarthi's_ pics/album_r/b.jpg", "cc"),
        ("C:/Users/Aarthi V/OneDrive/Desktop/aarthi's_ pics/album_r/c.jpeg", "brat"),
        ("C:/Users/Aarthi V/OneDrive/Desktop/aarthi's_ pics/album_r/o.jpg", "guts"),
        ("C:/Users/Aarthi V/OneDrive/Desktop/aarthi's_ pics/album_r/s.png", "ss")
    ]

    album_names = {
        "ttpd": "The Tortured Poets Department",
        "cc": "Cowboy Carter", 
        "brat": "Brat",
        "guts": "Guts",
        "ss": "Short n Sweet"
    }

    album_widgets = {}  # To keep track of rating labels for refresh

    def refresh_album_display(title):
        """Refresh the rating display for a specific album"""
        if title in album_widgets:
            rating_label = album_widgets[title]
            album_rating = get_album_rating(title)
            rating_text = f"{'★' * int(album_rating)}{'☆' * (5 - int(album_rating))} ({album_rating}/5)"
            rating_label.config(text=rating_text)

    for idx, (path, title) in enumerate(image_info):
        try:
            album_container = tk.Frame(image_frame, bg='#0f3460', relief='solid', bd=2)
            album_container.grid(row=0, column=idx, padx=15, pady=10)

            # Album rating display
            album_rating = get_album_rating(title)
            rating_text = f"{'★' * int(album_rating)}{'☆' * (5 - int(album_rating))} ({album_rating}/5)"
            rating_label = tk.Label(album_container, text=rating_text,
                                  font=('Arial', 8), bg='#0f3460', fg='#ffd700')
            rating_label.pack(pady=(5, 0))
            
            # Store reference for refresh
            album_widgets[title] = rating_label

            img = Image.open(path).resize((120, 120))
            tk_img = ImageTk.PhotoImage(img)
            album_images.append(tk_img)

            btn = tk.Button(album_container, image=tk_img,
                            bd=0, bg='#0f3460', cursor='hand2')
            btn.image = tk_img
            btn.pack(padx=5, pady=5)

            # Click to rate album
            btn.bind("<Button-1>", lambda e, t=title, n=album_names.get(title, title): 
                     open_album_rating_window(t, n, lambda: refresh_album_display(t)))
            
            Label(album_container, text=album_names.get(title, title),
                  font=('Arial', 9, 'bold'),
                  bg='#0f3460', fg='white').pack(pady=(0, 5))
        except Exception as e:
            print(f"Error loading {path}: {e}")

# --- Main UI ---
ml1 = Label(text="Album Rater", font=df, bg="rosy brown")
ml1.grid(row=1, column=1, sticky='nsew')

b = Button(root, text="Profile", command=profile, font=df1, height=1, bg="dark slate blue", fg="linen")
b.place(x=1200, y=10)

b1 = tk.Button(root, text="Albums", font=df1, height=1, bg="dark slate blue", fg="linen", command=mainpage)
b1.place(x=1400, y=10)

root.mainloop()
