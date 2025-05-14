import psycopg2
from psycopg2 import sql, errors
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QStackedWidget,
                             QTextEdit, QHBoxLayout, QScrollArea, QFrame, QDialog, QListWidgetItem, QListWidget,
                             QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt
import datetime
import configparser
import os


# Read database configuration from ini file
config = configparser.ConfigParser()
config_file = 'config.ini'

# Create default config file if it doesn't exist
if not os.path.exists(config_file):
    config['DATABASE'] = {
        'dbname': 'ProjectDB',
        'user': 'postgres',
        'password': '2023494',
        'host': 'localhost'
    }

    with open(config_file, 'w') as f:
        config.write(f)
    print(f"Created default config file: {config_file}")

# Read configuration
config.read(config_file)

# Database connection parameters
DB_PARAMS = {
    'dbname': config.get('DATABASE', 'dbname'),
    'user': config.get('DATABASE', 'user'),
    'password': config.get('DATABASE', 'password'),
    'host': config.get('DATABASE', 'host')
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
                query = sql.SQL("SELECT username FROM users WHERE username = %s AND password = %s")
                cur.execute(query, (username, password))
                user = cur.fetchone()
                if user:
                    return True, "Login successful", username
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
                query = sql.SQL("INSERT INTO posts (username, content) VALUES (%s, %s)")
                cur.execute(query, (username, content))
                conn.commit()
                return True, "Post created successfully"
    except errors.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def delete_post(post_id, username):
    """Delete a post from the database if the user is the owner"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # First check if the user owns the post
                query = sql.SQL("SELECT username FROM posts WHERE id = %s")
                cur.execute(query, (post_id,))
                result = cur.fetchone()

                if not result:
                    return False, "Post not found"

                if result[0] != username:
                    return False, "You can only delete your own posts"

                # Delete the post
                query = sql.SQL("DELETE FROM posts WHERE id = %s")
                cur.execute(query, (post_id,))
                conn.commit()
                return True, "Post deleted successfully"
    except errors.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_all_posts():
    """Retrieve all posts with usernames"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
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


def follow_user(follower, following):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT follow_user(%s, %s)", (follower, following))
                result = cur.fetchone()[0]
                conn.commit()
                return result, "Followed successfully" if result else "Already following"
    except Exception as e:
        return False, f"Error: {str(e)}"


def unfollow_user(follower, following):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT unfollow_user(%s, %s)", (follower, following))
                result = cur.fetchone()[0]
                conn.commit()
                return result, "Unfollowed successfully" if result else "Not following"
    except Exception as e:
        return False, f"Error: {str(e)}"


def is_following(follower, following):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT is_following(%s, %s)", (follower, following))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"Error checking follow status: {e}")
        return False


def get_following(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_following(%s)", (username,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting following list: {e}")
        return []


def get_followers(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_followers(%s)", (username,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting followers list: {e}")
        return []


def get_followed_posts(username):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_followed_posts(%s)", (username,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting followed posts: {e}")
        return []


def send_message(sender, receiver, content):
    """Send a direct message from sender to receiver"""
    if not content.strip():
        return False, "Message content cannot be empty"

    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT send_message(%s, %s, %s)", (sender, receiver, content))
                conn.commit()
                return True, "Message sent successfully"
    except Exception as e:
        return False, f"Error sending message: {str(e)}"


def get_conversation(user1, user2):
    """Get conversation between two users"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_conversation(%s, %s)", (user1, user2))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting conversation: {e}")
        return []


def get_user_conversations(username):
    """Get all conversations for a user"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_user_conversations(%s)", (username,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting user conversations: {e}")
        return []


def check_admin_credentials(username, password):
    """Check if the credentials match the admin account"""
    return username == "umbreon" and password == "3141592654"


def get_all_users():
    """Get all users from the database"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT username, password FROM users")
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting users: {e}")
        return []


def get_all_posts_admin():
    """Get all posts with usernames for admin view"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT id, username, content, created_at 
                    FROM posts
                    ORDER BY created_at DESC
                """)
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting posts: {e}")
        return []


def delete_user_admin(username):
    """Delete a user and move to recently_deleted_users"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # First get user data
                cur.execute("SELECT username, password FROM users WHERE username = %s", (username,))
                user_data = cur.fetchone()
                if not user_data:
                    return False, "User not found"

                # Get and move user's posts to recently_deleted_posts
                cur.execute("""
                    INSERT INTO recently_deleted_posts (id, username, content, created_at, deleted_at)
                    SELECT id, username, content, created_at, CURRENT_TIMESTAMP
                    FROM posts
                    WHERE username = %s
                """, (username,))

                # Delete related records
                # Delete follows where user is follower
                cur.execute("DELETE FROM follows WHERE follower_username = %s", (username,))
                # Delete follows where user is following
                cur.execute("DELETE FROM follows WHERE following_username = %s", (username,))
                # Delete user's posts
                cur.execute("DELETE FROM posts WHERE username = %s", (username,))
                # Delete conversations
                cur.execute("DELETE FROM conversations WHERE user1_username = %s OR user2_username = %s",
                            (username, username))
                # Delete direct messages
                cur.execute("DELETE FROM direct_messages WHERE sender_username = %s OR receiver_username = %s",
                            (username, username))

                # Delete from users first
                cur.execute("DELETE FROM users WHERE username = %s", (username,))

                # Then insert into recently_deleted_users
                cur.execute("""
                    INSERT INTO recently_deleted_users (username, password, deleted_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                """, user_data)

                conn.commit()
                return True, "User deleted successfully"
    except Exception as e:
        return False, f"Error deleting user: {str(e)}"


def delete_post_admin(post_id):
    """Delete a post and move to recently_deleted_posts"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # First get post data
                cur.execute("""
                    SELECT id, username, content, created_at 
                    FROM posts WHERE id = %s
                """, (post_id,))
                post_data = cur.fetchone()
                if not post_data:
                    return False, "Post not found"

                # Insert into recently_deleted_posts
                cur.execute("""
                    INSERT INTO recently_deleted_posts (id, username, content, created_at, deleted_at)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, post_data)

                # Delete from posts
                cur.execute("DELETE FROM posts WHERE id = %s", (post_id,))
                conn.commit()
                return True, "Post deleted successfully"
    except Exception as e:
        return False, f"Error deleting post: {str(e)}"


def get_recently_deleted_users():
    """Get all recently deleted users"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT username, deleted_at 
                    FROM recently_deleted_users
                    ORDER BY deleted_at DESC
                """)
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting recently deleted users: {e}")
        return []


def get_recently_deleted_posts():
    """Get all recently deleted posts"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT id, username, content, created_at, deleted_at 
                    FROM recently_deleted_posts
                    ORDER BY deleted_at DESC
                """)
                cur.execute(query)
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting recently deleted posts: {e}")
        return []


def recover_user(username):
    """Recover a user from recently_deleted_users"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # Get user data
                cur.execute("""
                    SELECT username, password 
                    FROM recently_deleted_users 
                    WHERE username = %s
                """, (username,))
                user_data = cur.fetchone()
                if not user_data:
                    return False, "User not found in deleted users"

                # Insert back into users
                cur.execute("""
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                """, user_data)

                # Recover user's posts
                cur.execute("""
                    INSERT INTO posts (id, username, content, created_at)
                    SELECT id, username, content, created_at
                    FROM recently_deleted_posts
                    WHERE username = %s
                """, (username,))

                # Delete from recently_deleted_users
                cur.execute("DELETE FROM recently_deleted_users WHERE username = %s", (username,))
                # Delete from recently_deleted_posts
                cur.execute("DELETE FROM recently_deleted_posts WHERE username = %s", (username,))

                conn.commit()
                return True, "User and their posts recovered successfully"
    except Exception as e:
        return False, f"Error recovering user: {str(e)}"


def recover_post(post_id):
    """Recover a post from recently_deleted_posts"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # Get post data
                cur.execute("""
                    SELECT id, username, content, created_at 
                    FROM recently_deleted_posts 
                    WHERE id = %s
                """, (post_id,))
                post_data = cur.fetchone()
                if not post_data:
                    return False, "Post not found in deleted posts"

                # Insert back into posts
                cur.execute("""
                    INSERT INTO posts (id, username, content, created_at)
                    VALUES (%s, %s, %s, %s)
                """, post_data)

                # Delete from recently_deleted_posts
                cur.execute("DELETE FROM recently_deleted_posts WHERE id = %s", (post_id,))
                conn.commit()
                return True, "Post recovered successfully"
    except Exception as e:
        return False, f"Error recovering post: {str(e)}"


def permanently_delete_user(username):
    """Permanently delete a user from recently_deleted_users"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM recently_deleted_users WHERE username = %s", (username,))
                conn.commit()
                return True, "User permanently deleted"
    except Exception as e:
        return False, f"Error permanently deleting user: {str(e)}"


def permanently_delete_post(post_id):
    """Permanently delete a post from recently_deleted_posts"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM recently_deleted_posts WHERE id = %s", (post_id,))
                conn.commit()
                return True, "Post permanently deleted"
    except Exception as e:
        return False, f"Error permanently deleting post: {str(e)}"


def like_post(post_id, username):
    """Like a post"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    INSERT INTO likes (post_id, username)
                    VALUES (%s, %s)
                    ON CONFLICT (post_id, username) DO NOTHING
                    RETURNING id
                """)
                cur.execute(query, (post_id, username))
                result = cur.fetchone()
                conn.commit()
                return True, "Post liked successfully" if result else "Already liked"
    except Exception as e:
        return False, f"Error liking post: {str(e)}"


def unlike_post(post_id, username):
    """Unlike a post"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("DELETE FROM likes WHERE post_id = %s AND username = %s")
                cur.execute(query, (post_id, username))
                conn.commit()
                return True, "Post unliked successfully"
    except Exception as e:
        return False, f"Error unliking post: {str(e)}"


def is_post_liked(post_id, username):
    """Check if a post is liked by a user"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT EXISTS(SELECT 1 FROM likes WHERE post_id = %s AND username = %s)")
                cur.execute(query, (post_id, username))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"Error checking like status: {e}")
        return False


def get_like_count(post_id):
    """Get the number of likes for a post"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT COUNT(*) FROM likes WHERE post_id = %s")
                cur.execute(query, (post_id,))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"Error getting like count: {e}")
        return 0


def add_reply(post_id, username, content, parent_reply_id=None):
    """Add a reply to a post"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    INSERT INTO replies (post_id, username, content, parent_reply_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """)
                cur.execute(query, (post_id, username, content, parent_reply_id))
                conn.commit()
                return True, "Reply added successfully"
    except Exception as e:
        return False, f"Error adding reply: {str(e)}"


def get_replies(post_id):
    """Get all replies for a post"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("""
                    SELECT r.id, r.username, r.content, r.created_at, r.parent_reply_id,
                           COALESCE(p.username, '') as parent_username
                    FROM replies r
                    LEFT JOIN replies p ON r.parent_reply_id = p.id
                    WHERE r.post_id = %s
                    ORDER BY r.created_at ASC
                """)
                cur.execute(query, (post_id,))
                return cur.fetchall()
    except Exception as e:
        print(f"Error getting replies: {e}")
        return []


def delete_reply(reply_id, username):
    """Delete a reply if the user is the owner"""
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                # First check if the user owns the reply
                query = sql.SQL("SELECT username FROM replies WHERE id = %s")
                cur.execute(query, (reply_id,))
                result = cur.fetchone()

                if not result:
                    return False, "Reply not found"

                if result[0] != username:
                    return False, "You can only delete your own replies"

                # Delete the reply
                query = sql.SQL("DELETE FROM replies WHERE id = %s")
                cur.execute(query, (reply_id,))
                conn.commit()
                return True, "Reply deleted successfully"
    except Exception as e:
        return False, f"Error deleting reply: {str(e)}"


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
        self.register_button.clicked.connect(self.switch_to_register)

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

        # Check for admin credentials first
        if check_admin_credentials(username, password):
            self.stacked_widget.setCurrentIndex(3)  # Switch to admin interface
            self.username_input.clear()
            self.password_input.clear()
            return

        # Regular user login
        success, message, username = check_credentials(username, password)

        msg = QMessageBox()
        if success:
            msg.setIcon(QMessageBox.Information)
            msg.setText(message)
            msg.exec_()
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
        self.current_profile_view = None
        self.is_dark_mode = True
        self.init_ui()

    def set_user(self, username):
        self.username = username
        self.welcome_label.setText(f"Welcome, {self.username}!")
        self.refresh_feed()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add header with welcome message and settings button
        header_layout = QHBoxLayout()
        self.welcome_label = QLabel("Welcome to the Application!")
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(self.settings_btn)
        layout.addLayout(header_layout)

        self.messages_btn = QPushButton("Messages")
        self.messages_btn.clicked.connect(self.show_messages)
        layout.addWidget(self.messages_btn)

        self.profile_btn = QPushButton("My Profile")
        self.profile_btn.clicked.connect(self.show_own_profile)
        layout.addWidget(self.profile_btn)

        button_layout = QHBoxLayout()
        self.create_post_btn = QPushButton("Create Post")
        self.create_post_btn.clicked.connect(self.show_create_post)
        self.feed_btn = QPushButton("View Feed")
        self.feed_btn.clicked.connect(self.show_feed)
        self.following_feed_btn = QPushButton("Following Feed")
        self.following_feed_btn.clicked.connect(self.show_following_feed)
        button_layout.addWidget(self.create_post_btn)
        button_layout.addWidget(self.feed_btn)
        button_layout.addWidget(self.following_feed_btn)
        layout.addLayout(button_layout)

        self.main_stack = QStackedWidget()

        self.post_widget = QWidget()
        post_layout = QVBoxLayout()
        self.post_content = QTextEdit()
        self.post_content.setPlaceholderText("What's on your mind?")
        post_submit_btn = QPushButton("Post")
        post_submit_btn.clicked.connect(self.submit_post)
        post_layout.addWidget(self.post_content)
        post_layout.addWidget(post_submit_btn)
        self.post_widget.setLayout(post_layout)

        self.feed_widget = QWidget()
        feed_layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)
        feed_layout.addWidget(scroll)
        self.feed_widget.setLayout(feed_layout)

        self.main_stack.addWidget(self.post_widget)
        self.main_stack.addWidget(self.feed_widget)

        layout.addWidget(self.main_stack)
        self.setLayout(layout)
        self.apply_theme()

    def show_settings(self):
        """Show settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QVBoxLayout()

        # Theme settings
        theme_group = QWidget()
        theme_layout = QVBoxLayout()
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet("font-weight: bold;")
        theme_layout.addWidget(theme_label)

        theme_toggle = QPushButton("Dark Mode" if not self.is_dark_mode else "Light Mode")
        theme_toggle.clicked.connect(lambda: self.toggle_theme(theme_toggle))
        theme_layout.addWidget(theme_toggle)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("color: red;")
        logout_btn.clicked.connect(lambda: self.confirm_logout(dialog))
        layout.addWidget(logout_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def toggle_theme(self, button):
        """Toggle between dark and light mode"""
        self.is_dark_mode = not self.is_dark_mode
        button.setText("Dark Mode" if not self.is_dark_mode else "Light Mode")
        self.apply_theme()

    def apply_theme(self):
        """Apply the current theme to all widgets"""
        if self.is_dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3b3b3b;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4b4b4b;
                }
                QLineEdit, QTextEdit {
                    background-color: #3b3b3b;
                    border: 1px solid #555555;
                    color: #ffffff;
                    padding: 5px;
                }
                QLabel {
                    color: #ffffff;
                }
                QScrollArea {
                    border: 1px solid #555555;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QLineEdit, QTextEdit {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    color: #000000;
                    padding: 5px;
                }
                QLabel {
                    color: #000000;
                }
                QScrollArea {
                    border: 1px solid #cccccc;
                }
            """)

    def confirm_logout(self, settings_dialog):
        """Show confirmation dialog before logging out"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to logout?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            settings_dialog.accept()
            self.handle_logout()

    def handle_logout(self):
        # Clear the current user
        self.username = None
        # Clear any existing data
        self.post_content.clear()
        # Switch back to login screen
        self.stacked_widget.setCurrentIndex(1)
        # Clear the login form
        login_widget = self.stacked_widget.widget(1)
        login_widget.username_input.clear()
        login_widget.password_input.clear()

    def show_following_feed(self):
        self.main_stack.setCurrentIndex(1)
        self.refresh_feed(following_only=True)

    def show_create_post(self):
        self.main_stack.setCurrentIndex(0)

    def show_feed(self):
        self.main_stack.setCurrentIndex(1)
        self.refresh_feed()

    def show_messages(self):
        dialog = MessageDialog(self.username, self)
        dialog.exec_()

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

    def refresh_feed(self, following_only=False):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if following_only:
            posts = get_followed_posts(self.username)
            if not posts:
                no_posts_label = QLabel("No posts from people you follow yet.")
                self.scroll_layout.addWidget(no_posts_label)
                return
        else:
            posts = get_all_posts()
            if not posts:
                no_posts_label = QLabel("No posts yet. Be the first to post!")
                self.scroll_layout.addWidget(no_posts_label)
                return

        for post in posts:
            post_id, username, content, created_at = post
            post_widget = QWidget()
            post_layout = QVBoxLayout()

            header = QHBoxLayout()
            username_btn = QPushButton(username)
            username_btn.setStyleSheet("border: none; color: blue; text-align: left;")
            username_btn.clicked.connect(lambda _, u=username: self.show_user_profile(u))
            header.addWidget(username_btn)
            header.addStretch()

            # Add delete button if the post belongs to the current user
            if username == self.username:
                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("color: red;")
                delete_btn.clicked.connect(lambda _, pid=post_id: self.confirm_delete_post(pid))
                header.addWidget(delete_btn)

            header.addWidget(QLabel(created_at.strftime('%Y-%m-%d %H:%M')))

            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("padding: 5px;")

            # Add like button and count
            like_layout = QHBoxLayout()
            like_btn = QPushButton()
            like_btn.setCheckable(True)
            like_btn.setChecked(is_post_liked(post_id, self.username))
            like_btn.setText("Liked" if like_btn.isChecked() else "Like")
            like_btn.clicked.connect(lambda _, pid=post_id: self.toggle_like(pid))
            like_count = QLabel(str(get_like_count(post_id)))
            like_layout.addWidget(like_btn)
            like_layout.addWidget(like_count)
            like_layout.addStretch()

            # Add reply button
            reply_btn = QPushButton("Reply")
            reply_btn.clicked.connect(lambda _, pid=post_id: self.show_reply_dialog(pid))
            like_layout.addWidget(reply_btn)

            if username != self.username:
                follow_btn = QPushButton()
                follow_btn.setCheckable(True)
                follow_btn.setChecked(is_following(self.username, username))
                follow_btn.setText("Following" if follow_btn.isChecked() else "Follow")
                follow_btn.clicked.connect(lambda _, u=username: self.toggle_follow(u))
                post_layout.addWidget(follow_btn)

            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)

            post_layout.addLayout(header)
            post_layout.addWidget(content_label)
            post_layout.addLayout(like_layout)
            post_layout.addWidget(separator)

            # Add replies section
            replies = get_replies(post_id)
            if replies:
                replies_widget = QWidget()
                replies_layout = QVBoxLayout()
                replies_label = QLabel("Replies:")
                replies_layout.addWidget(replies_label)

                for reply in replies:
                    reply_id, reply_username, reply_content, reply_time, parent_id, parent_username = reply
                    reply_widget = QWidget()
                    reply_layout = QVBoxLayout()

                    reply_header = QHBoxLayout()
                    reply_username_btn = QPushButton(reply_username)
                    reply_username_btn.setStyleSheet("border: none; color: blue; text-align: left;")
                    reply_username_btn.clicked.connect(lambda _, u=reply_username: self.show_user_profile(u))
                    reply_header.addWidget(reply_username_btn)

                    if parent_username:
                        reply_header.addWidget(QLabel(f"replying to {parent_username}"))

                    if reply_username == self.username:
                        delete_reply_btn = QPushButton("Delete")
                        delete_reply_btn.setStyleSheet("color: red;")
                        delete_reply_btn.clicked.connect(lambda _, rid=reply_id: self.confirm_delete_reply(rid))
                        reply_header.addWidget(delete_reply_btn)

                    reply_header.addStretch()
                    reply_header.addWidget(QLabel(reply_time.strftime('%Y-%m-%d %H:%M')))

                    reply_content_label = QLabel(reply_content)
                    reply_content_label.setWordWrap(True)

                    reply_reply_btn = QPushButton("Reply")
                    reply_reply_btn.clicked.connect(
                        lambda _, pid=post_id, rid=reply_id: self.show_reply_dialog(pid, rid))

                    reply_layout.addLayout(reply_header)
                    reply_layout.addWidget(reply_content_label)
                    reply_layout.addWidget(reply_reply_btn)

                    reply_widget.setLayout(reply_layout)
                    replies_layout.addWidget(reply_widget)

                replies_widget.setLayout(replies_layout)
                post_layout.addWidget(replies_widget)

            post_widget.setLayout(post_layout)
            self.scroll_layout.addWidget(post_widget)

    def confirm_delete_post(self, post_id):
        """Show confirmation dialog before deleting a post"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to delete this post?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            success, message = delete_post(post_id, self.username)

            result_msg = QMessageBox()
            if success:
                result_msg.setIcon(QMessageBox.Information)
                self.refresh_feed()
            else:
                result_msg.setIcon(QMessageBox.Warning)

            result_msg.setText(message)
            result_msg.exec_()

    def toggle_follow(self, username):
        if is_following(self.username, username):
            success, message = unfollow_user(self.username, username)
        else:
            success, message = follow_user(self.username, username)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information if success else QMessageBox.Warning)
        msg.setText(message)
        msg.exec_()
        self.refresh_feed()
        if self.current_profile_view:
            self.show_user_profile(self.current_profile_view)

    def show_user_profile(self, username):
        self.current_profile_view = username
        profile_dialog = QDialog(self)
        profile_dialog.setWindowTitle(f"{username}'s Profile")
        layout = QVBoxLayout()

        header = QHBoxLayout()
        header.addWidget(QLabel(f"Username: {username}"))

        if username != self.username:
            message_btn = QPushButton("Message")
            message_btn.clicked.connect(lambda: self.open_message_to_user(username))
            header.addWidget(message_btn)

        if username != self.username:
            follow_btn = QPushButton()
            follow_btn.setCheckable(True)
            follow_btn.setChecked(is_following(self.username, username))
            follow_btn.setText("Following" if follow_btn.isChecked() else "Follow")
            follow_btn.clicked.connect(lambda: self.toggle_follow(username))
            header.addWidget(follow_btn)

        layout.addLayout(header)

        stats = QHBoxLayout()
        followers = get_followers(username)
        following = get_following(username)
        stats.addWidget(QLabel(f"Followers: {len(followers)}"))
        stats.addWidget(QLabel(f"Following: {len(following)}"))
        layout.addLayout(stats)

        posts_label = QLabel("Posts:")
        layout.addWidget(posts_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(scroll_content)

        user_posts = [p for p in get_all_posts() if p[1] == username]
        for post in user_posts:
            post_id, _, content, created_at = post
            post_widget = QWidget()
            post_layout = QVBoxLayout()

            content_label = QLabel(content)
            content_label.setWordWrap(True)
            timestamp_label = QLabel(created_at.strftime('%Y-%m-%d %H:%M'))

            post_layout.addWidget(content_label)
            post_layout.addWidget(timestamp_label)
            post_widget.setLayout(post_layout)
            scroll_layout.addWidget(post_widget)

        layout.addWidget(scroll)
        profile_dialog.setLayout(layout)
        profile_dialog.exec_()

    def open_message_to_user(self, username):
        dialog = MessageDialog(self.username, self)
        dialog.start_conversation(username)
        dialog.exec_()

    def show_own_profile(self):
        self.show_user_profile(self.username)

    def toggle_like(self, post_id):
        """Toggle like status for a post"""
        if is_post_liked(post_id, self.username):
            success, message = unlike_post(post_id, self.username)
        else:
            success, message = like_post(post_id, self.username)

        if success:
            self.refresh_feed()

    def show_reply_dialog(self, post_id, parent_reply_id=None):
        """Show dialog for adding a reply"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Reply")
        layout = QVBoxLayout()

        reply_input = QTextEdit()
        reply_input.setPlaceholderText("Write your reply...")
        layout.addWidget(reply_input)

        button_layout = QHBoxLayout()
        submit_btn = QPushButton("Submit")
        cancel_btn = QPushButton("Cancel")

        submit_btn.clicked.connect(
            lambda: self.submit_reply(post_id, reply_input.toPlainText().strip(), parent_reply_id, dialog))
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(submit_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def submit_reply(self, post_id, content, parent_reply_id, dialog):
        """Submit a reply to a post"""
        if not content:
            QMessageBox.warning(self, "Warning", "Reply content cannot be empty")
            return

        success, message = add_reply(post_id, self.username, content, parent_reply_id)

        msg = QMessageBox()
        if success:
            msg.setIcon(QMessageBox.Information)
            dialog.accept()
            self.refresh_feed()
        else:
            msg.setIcon(QMessageBox.Warning)

        msg.setText(message)
        msg.exec_()

    def confirm_delete_reply(self, reply_id):
        """Show confirmation dialog before deleting a reply"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to delete this reply?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            success, message = delete_reply(reply_id, self.username)

            result_msg = QMessageBox()
            if success:
                result_msg.setIcon(QMessageBox.Information)
                self.refresh_feed()
            else:
                result_msg.setIcon(QMessageBox.Warning)

            result_msg.setText(message)
            result_msg.exec_()


class MessageDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.current_conversation = None
        self.setWindowTitle("Messages")
        self.setMinimumSize(600, 400)
        self.init_ui()
        self.load_conversations()

    def init_ui(self):
        layout = QHBoxLayout()

        # Left panel - conversation list
        self.conversation_list = QListWidget()
        self.conversation_list.itemClicked.connect(self.open_conversation)
        layout.addWidget(self.conversation_list, 1)

        # Right panel - conversation view
        right_panel = QVBoxLayout()

        # Conversation header
        self.conversation_header = QLabel("Select a conversation")
        right_panel.addWidget(self.conversation_header)

        # Messages display
        self.messages_display = QTextEdit()
        self.messages_display.setReadOnly(True)
        right_panel.addWidget(self.messages_display, 1)

        # Message input area
        input_layout = QHBoxLayout()
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(80)
        self.message_input.setPlaceholderText("Type your message here...")
        input_layout.addWidget(self.message_input, 1)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        right_panel.addLayout(input_layout)
        layout.addLayout(right_panel, 2)

        self.setLayout(layout)

    def load_conversations(self):
        self.conversation_list.clear()
        conversations = get_user_conversations(self.username)

        for conv in conversations:
            other_user, last_msg, timestamp, unread = conv
            item_text = f"{other_user}"
            if unread > 0:
                item_text += f" ({unread} new)"

            item = QListWidgetItem(item_text)
            if unread > 0:
                item.setForeground(Qt.blue)
            self.conversation_list.addItem(item)

    def start_conversation(self, username):
        # Find if conversation already exists
        for i in range(self.conversation_list.count()):
            item = self.conversation_list.item(i)
            if item.text().startswith(username):
                self.conversation_list.setCurrentItem(item)
                self.open_conversation(item)
                return

        # If not, create a new one
        self.current_conversation = username
        self.update_conversation_view()

    def open_conversation(self, item):
        other_user = item.text().split()[0]  # Remove "(X new)" if present
        self.current_conversation = other_user
        self.update_conversation_view()

    def update_conversation_view(self):
        if not self.current_conversation:
            return

        self.conversation_header.setText(f"Conversation with {self.current_conversation}")
        self.messages_display.clear()

        messages = get_conversation(self.username, self.current_conversation)

        for msg in messages:
            msg_id, sender, content, timestamp, is_read = msg
            alignment = "left" if sender != self.username else "right"
            color = "#e1f5fe" if sender != self.username else "#e8f5e9"

            message_html = f"""
            <div style="margin: 5px; padding: 8px; background-color: {color}; 
                        border-radius: 8px; text-align: {alignment};">
                <div><b>{sender}:</b></div>
                <div>{content}</div>
                <div style="font-size: small; color: gray;">{timestamp.strftime('%Y-%m-%d %H:%M')}</div>
            </div>
            """
            self.messages_display.append(message_html)

        # Scroll to bottom
        self.messages_display.verticalScrollBar().setValue(
            self.messages_display.verticalScrollBar().maximum()
        )

    def send_message(self):
        if not self.current_conversation:
            QMessageBox.warning(self, "Warning", "No conversation selected")
            return

        content = self.message_input.toPlainText().strip()
        if not content:
            return

        success, message = send_message(self.username, self.current_conversation, content)
        if success:
            self.message_input.clear()
            self.update_conversation_view()
            self.load_conversations()
        else:
            QMessageBox.warning(self, "Error", message)


class AdminApp(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Header
        header = QHBoxLayout()
        self.title_label = QLabel("Admin Dashboard")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.handle_logout)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.logout_btn)
        layout.addLayout(header)

        # View selection buttons
        view_layout = QHBoxLayout()
        self.users_btn = QPushButton("Users")
        self.posts_btn = QPushButton("Posts")
        self.recently_deleted_btn = QPushButton("Recently Deleted")

        self.users_btn.clicked.connect(lambda: self.show_view("users"))
        self.posts_btn.clicked.connect(lambda: self.show_view("posts"))
        self.recently_deleted_btn.clicked.connect(lambda: self.show_view("recently_deleted"))

        view_layout.addWidget(self.users_btn)
        view_layout.addWidget(self.posts_btn)
        view_layout.addWidget(self.recently_deleted_btn)
        layout.addLayout(view_layout)

        # Table view
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Content", "Date"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Action buttons
        button_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Delete")
        self.recover_btn = QPushButton("Recover")
        self.permanent_delete_btn = QPushButton("Delete Permanently")

        self.delete_btn.clicked.connect(self.delete_item)
        self.recover_btn.clicked.connect(self.recover_item)
        self.permanent_delete_btn.clicked.connect(self.permanent_delete_item)

        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.recover_btn)
        button_layout.addWidget(self.permanent_delete_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.current_view = "users"
        self.show_view("users")

    def show_view(self, view_type):
        self.current_view = view_type
        self.table.setRowCount(0)

        if view_type == "users":
            users = get_all_users()
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["Username", "Password"])
            for user in users:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(user[0]))
                self.table.setItem(row, 1, QTableWidgetItem(user[1]))

        elif view_type == "posts":
            posts = get_all_posts_admin()
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["ID", "Username", "Content", "Date"])
            for post in posts:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(post[0])))
                self.table.setItem(row, 1, QTableWidgetItem(post[1]))
                self.table.setItem(row, 2, QTableWidgetItem(post[2]))
                self.table.setItem(row, 3, QTableWidgetItem(str(post[3])))

        elif view_type == "recently_deleted":
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["ID", "Username", "Content", "Deleted At", "Type"])

            # Show recently deleted users
            deleted_users = get_recently_deleted_users()
            for user in deleted_users:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(""))
                self.table.setItem(row, 1, QTableWidgetItem(user[0]))
                self.table.setItem(row, 2, QTableWidgetItem(""))
                self.table.setItem(row, 3, QTableWidgetItem(str(user[1])))
                self.table.setItem(row, 4, QTableWidgetItem("User"))

            # Show recently deleted posts
            deleted_posts = get_recently_deleted_posts()
            for post in deleted_posts:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(post[0])))
                self.table.setItem(row, 1, QTableWidgetItem(post[1]))
                self.table.setItem(row, 2, QTableWidgetItem(post[2]))
                self.table.setItem(row, 3, QTableWidgetItem(str(post[4])))
                self.table.setItem(row, 4, QTableWidgetItem("Post"))

        # Update button visibility
        self.delete_btn.setVisible(view_type != "recently_deleted")
        self.recover_btn.setVisible(view_type == "recently_deleted")
        self.permanent_delete_btn.setVisible(view_type == "recently_deleted")

    def delete_item(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an item to delete")
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to delete this item?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            if self.current_view == "users":
                username = self.table.item(current_row, 0).text()
                success, message = delete_user_admin(username)
            else:
                post_id = int(self.table.item(current_row, 0).text())
                success, message = delete_post_admin(post_id)

            if success:
                self.show_view(self.current_view)
            QMessageBox.information(self, "Result", message)

    def recover_item(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an item to recover")
            return

        item_type = self.table.item(current_row, 4).text()
        if item_type == "User":
            username = self.table.item(current_row, 1).text()
            success, message = recover_user(username)
        else:
            post_id = int(self.table.item(current_row, 0).text())
            success, message = recover_post(post_id)

        if success:
            self.show_view("recently_deleted")
        QMessageBox.information(self, "Result", message)

    def permanent_delete_item(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select an item to delete permanently")
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to permanently delete this item? This action cannot be undone.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            item_type = self.table.item(current_row, 4).text()
            if item_type == "User":
                username = self.table.item(current_row, 1).text()
                success, message = permanently_delete_user(username)
            else:
                post_id = int(self.table.item(current_row, 0).text())
                success, message = permanently_delete_post(post_id)

            if success:
                self.show_view("recently_deleted")
            QMessageBox.information(self, "Result", message)

    def handle_logout(self):
        self.stacked_widget.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication([])
    stacked_widget = QStackedWidget()

    registration_app = RegistrationApp(stacked_widget)
    login_app = LoginApp(stacked_widget)
    main_app = MainApp(stacked_widget)
    admin_app = AdminApp(stacked_widget)  # Add admin app

    stacked_widget.addWidget(registration_app)
    stacked_widget.addWidget(login_app)
    stacked_widget.addWidget(main_app)
    stacked_widget.addWidget(admin_app)  # Add admin app to stacked widget

    stacked_widget.setCurrentIndex(1)
    stacked_widget.setWindowTitle('Social Media App')
    stacked_widget.setFixedSize(500, 400)
    stacked_widget.show()

    app.exec_()