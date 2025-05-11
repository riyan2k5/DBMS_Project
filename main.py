import psycopg2
from psycopg2 import sql, errors
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QStackedWidget,
                             QTextEdit, QHBoxLayout, QScrollArea, QFrame, QDialog, QListWidgetItem, QListWidget)
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
        self.init_ui()

    def set_user(self, username):
        self.username = username
        self.welcome_label.setText(f"Welcome, {self.username}!")
        self.refresh_feed()

    def init_ui(self):
        layout = QVBoxLayout()

        self.welcome_label = QLabel("Welcome to the Application!")
        layout.addWidget(self.welcome_label)

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
            header.addWidget(QLabel(created_at.strftime('%Y-%m-%d %H:%M')))

            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("padding: 5px;")

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
            post_layout.addWidget(separator)

            post_widget.setLayout(post_layout)
            self.scroll_layout.addWidget(post_widget)

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


if __name__ == '__main__':
    app = QApplication([])
    stacked_widget = QStackedWidget()

    registration_app = RegistrationApp(stacked_widget)
    login_app = LoginApp(stacked_widget)
    main_app = MainApp(stacked_widget)

    stacked_widget.addWidget(registration_app)
    stacked_widget.addWidget(login_app)
    stacked_widget.addWidget(main_app)

    stacked_widget.setCurrentIndex(1)
    stacked_widget.setWindowTitle('Social Media App')
    stacked_widget.setFixedSize(500, 400)
    stacked_widget.show()

    app.exec_()