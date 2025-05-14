from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                             QStackedWidget, QTextEdit, QScrollArea, QFrame, QDialog,
                             QMessageBox)
from PyQt5.QtCore import Qt
from database import (create_post, get_all_posts, get_followed_posts, delete_post,
                      follow_user, unfollow_user, is_following, get_followers, get_following,
                      like_post, unlike_post, is_post_liked, get_like_count,
                      add_reply, get_replies, delete_reply)
from .message_dialog import MessageDialog

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
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QVBoxLayout()

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

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("color: red;")
        logout_btn.clicked.connect(lambda: self.confirm_logout(dialog))
        layout.addWidget(logout_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def toggle_theme(self, button):
        self.is_dark_mode = not self.is_dark_mode
        button.setText("Dark Mode" if not self.is_dark_mode else "Light Mode")
        self.apply_theme()

    def apply_theme(self):
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
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to logout?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            settings_dialog.accept()
            self.handle_logout()

    def handle_logout(self):
        self.username = None
        self.post_content.clear()
        self.stacked_widget.setCurrentIndex(1)
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

            if username == self.username:
                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("color: red;")
                delete_btn.clicked.connect(lambda _, pid=post_id: self.confirm_delete_post(pid))
                header.addWidget(delete_btn)

            header.addWidget(QLabel(created_at.strftime('%Y-%m-%d %H:%M')))

            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("padding: 5px;")

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
        if is_post_liked(post_id, self.username):
            success, message = unlike_post(post_id, self.username)
        else:
            success, message = like_post(post_id, self.username)

        if success:
            self.refresh_feed()

    def show_reply_dialog(self, post_id, parent_reply_id=None):
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