CREATE TABLE login_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    name TEXT,
    login_time TEXT,
    FOREIGN KEY (email) REFERENCES users(email)
)
