import psycopg2
from psycopg2 import sql, errors
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QStackedWidget,
                             QTextEdit, QHBoxLayout, QScrollArea, QFrame)
from PyQt5.QtCore import Qt
import datetime

# Database connection parameters
DB_PARAMS = {
    'dbname': 'ProjectDB',
    'user': 'postgres',
    'password': '2023494',
    'host': 'localhost'
}


def register_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be blank"

    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("INSERT INTO users (username, password) VALUES (%s, %s)")
                cur.execute(query, (username, password))
                conn.commit()
                return True, "User registered successfully"
    except errors.UniqueViolation:
        return False, "Username already exists"
    except errors.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def check_credentials(username, password):
    """Check if username and password match in the database"""
    if not username or not password:
        return False, "Username and password cannot be blank"


    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # Changed to just check if user exists since we don't have an ID
                query = sql.SQL("SELECT username FROM users WHERE username = %s AND password = %s")
                cur.execute(query, (username, password))
                user = cur.fetchone()
                if user:
                    return True, "Login successful", username  # Return username instead of ID
                else:
                    return False, "Invalid username or password", None
    except errors.DatabaseError as e:
        return False, f"Database error: {e}", None
    except Exception as e:
        return False, f"Unexpected error: {e}", None


def create_post(username, content):
    """Create a new post in the database"""
    if not content.strip():
        return False, "Post content cannot be empty"

    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # Changed to use username directly since we don't have user_id
                query = sql.SQL("INSERT INTO posts (username, content) VALUES (%s, %s)")
                cur.execute(query, (username, content))
                conn.commit()
                return True, "Post created successfully"
    except errors.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_all_posts():
    """Retrieve all posts with usernames"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # Simplified query since we're storing username directly in posts
                query = sql.SQL("""
                    SELECT id, username, content, created_at 
                    FROM posts
                    ORDER BY created_at DESC
                """)
                cur.execute(query)
                return cur.fetchall()
    except errors.DatabaseError as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


class RegistrationApp(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('User Registration')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_label = QLabel('Username:')
        self.username_input = QLineEdit()

        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton('Register')
        self.register_button.clicked.connect(self.handle_register)

        self.login_button = QPushButton('Already have an account? Login')
        self.login_button.clicked.connect(self.switch_to_login)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        success, message = register_user(username, password)

        msg = QMessageBox()
        if success:
            msg.setIcon(QMessageBox.Information)
            self.username_input.clear()
            self.password_input.clear()
        else:
            msg.setIcon(QMessageBox.Warning)

        msg.setText(message)
        msg.exec_()

    def switch_to_login(self):
        self.stacked_widget.setCurrentIndex(1)
        self.username_input.clear()
        self.password_input.clear()


class LoginApp(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('User Login')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_label = QLabel('Username:')
        self.username_input = QLineEdit()

        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.handle_login)

        self.register_button = QPushButton('Need an account? Register')
        self.register_button.clicked.connect(self.switch_to_register)  # This line was correct

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def switch_to_register(self):
        self.stacked_widget.setCurrentIndex(0)
        self.username_input.clear()
        self.password_input.clear()

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Username and password cannot be blank")
            msg.exec_()
            return

        success, message, username = check_credentials(username, password)

        msg = QMessageBox()
        if success:
            msg.setIcon(QMessageBox.Information)
            msg.setText(message)
            msg.exec_()
            # Switch to main app and pass the username
            self.stacked_widget.widget(2).set_user(username)
            self.stacked_widget.setCurrentIndex(2)
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText(message)
            msg.exec_()


class MainApp(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.username = None
        self.init_ui()

    def set_user(self, username):
        """Set the current user information"""
        self.username = username
        self.welcome_label.setText(f"Welcome, {self.username}!")
        self.refresh_feed()

    def init_ui(self):
        layout = QVBoxLayout()

        # Welcome label
        self.welcome_label = QLabel("Welcome to the Application!")
        layout.addWidget(self.welcome_label)

        # Tab buttons
        button_layout = QHBoxLayout()
        self.create_post_btn = QPushButton("Create Post")
        self.create_post_btn.clicked.connect(self.show_create_post)
        self.feed_btn = QPushButton("View Feed")
        self.feed_btn.clicked.connect(self.show_feed)
        button_layout.addWidget(self.create_post_btn)
        button_layout.addWidget(self.feed_btn)
        layout.addLayout(button_layout)

        # Stacked widget for different views
        self.main_stack = QStackedWidget()

        # Create post view
        self.post_widget = QWidget()
        post_layout = QVBoxLayout()
        self.post_content = QTextEdit()
        self.post_content.setPlaceholderText("What's on your mind?")
        post_submit_btn = QPushButton("Post")
        post_submit_btn.clicked.connect(self.submit_post)
        post_layout.addWidget(self.post_content)
        post_layout.addWidget(post_submit_btn)
        self.post_widget.setLayout(post_layout)

        # Feed view
        self.feed_widget = QWidget()
        feed_layout = QVBoxLayout()

        # Scroll area for feed
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)

        feed_layout.addWidget(scroll)
        self.feed_widget.setLayout(feed_layout)

        # Add widgets to stack
        self.main_stack.addWidget(self.post_widget)
        self.main_stack.addWidget(self.feed_widget)

        layout.addWidget(self.main_stack)
        self.setLayout(layout)

    def show_create_post(self):
        self.main_stack.setCurrentIndex(0)

    def show_feed(self):
        self.main_stack.setCurrentIndex(1)
        self.refresh_feed()

    def submit_post(self):
        content = self.post_content.toPlainText().strip()
        success, message = create_post(self.username, content)

        msg = QMessageBox()
        if success:
            msg.setIcon(QMessageBox.Information)
            self.post_content.clear()
            self.refresh_feed()
        else:
            msg.setIcon(QMessageBox.Warning)

        msg.setText(message)
        msg.exec_()

    def refresh_feed(self):
        # Clear existing feed
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)

        # Get all posts from database
        posts = get_all_posts()

        if not posts:
            no_posts_label = QLabel("No posts yet. Be the first to post!")
            self.scroll_layout.addWidget(no_posts_label)
            return

        for post in posts:
            post_id, username, content, created_at = post
            post_widget = QWidget()
            post_layout = QVBoxLayout()

            # Header with username and timestamp
            header = QLabel(f"{username} • {created_at.strftime('%Y-%m-%d %H:%M')}")
            header.setStyleSheet("font-weight: bold; color: #555;")

            # Content
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("padding: 5px;")

            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)

            post_layout.addWidget(header)
            post_layout.addWidget(content_label)
            post_layout.addWidget(separator)

            post_widget.setLayout(post_layout)
            self.scroll_layout.addWidget(post_widget)


if __name__ == '__main__':
    app = QApplication([])

    # Create a stacked widget to handle multiple screens
    stacked_widget = QStackedWidget()

    # Create and add the registration and login screens
    registration_app = RegistrationApp(stacked_widget)
    login_app = LoginApp(stacked_widget)
    main_app = MainApp(stacked_widget)

    stacked_widget.addWidget(registration_app)
    stacked_widget.addWidget(login_app)
    stacked_widget.addWidget(main_app)

    stacked_widget.setCurrentIndex(1)  # Start with login screen
    stacked_widget.setWindowTitle('Social Media App')
    stacked_widget.setFixedSize(500, 400)
    stacked_widget.show()

    app.exec_()