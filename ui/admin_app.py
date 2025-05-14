from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QDialog, QMessageBox,
                             QApplication)
from PyQt5.QtCore import Qt
from database import (get_all_users, get_all_posts_admin, delete_user_admin, delete_post_admin,
                      get_recently_deleted_users, get_recently_deleted_posts,
                      recover_user, recover_post, permanently_delete_user, permanently_delete_post)
from firebase_backup import backup_all_tables_to_firebase, firebase_ref

class AdminApp(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        header = QHBoxLayout()
        self.title_label = QLabel("Admin Dashboard")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.handle_logout)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.logout_btn)
        layout.addLayout(header)

        view_layout = QHBoxLayout()
        self.users_btn = QPushButton("Users")
        self.posts_btn = QPushButton("Posts")
        self.recently_deleted_btn = QPushButton("Recently Deleted")

        self.backup_btn = QPushButton("Backup to Firebase")
        self.backup_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.backup_btn.clicked.connect(self.backup_to_firebase)

        self.users_btn.clicked.connect(lambda: self.show_view("users"))
        self.posts_btn.clicked.connect(lambda: self.show_view("posts"))
        self.recently_deleted_btn.clicked.connect(lambda: self.show_view("recently_deleted"))

        view_layout.addWidget(self.users_btn)
        view_layout.addWidget(self.posts_btn)
        view_layout.addWidget(self.recently_deleted_btn)
        view_layout.addWidget(self.backup_btn)
        layout.addLayout(view_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Content", "Date"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

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

    def backup_to_firebase(self):
        if not firebase_ref:
            QMessageBox.warning(self, "Warning",
                                "Firebase not initialized. Please check your credentials file.")
            return

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Are you sure you want to backup the database to Firebase?")
        msg.setInformativeText("This will overwrite any existing backup.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("Backup in Progress")
            progress_dialog.setModal(True)
            progress_layout = QVBoxLayout()

            progress_label = QLabel("Backing up database to Firebase...")
            progress_label.setAlignment(Qt.AlignCenter)
            progress_layout.addWidget(progress_label)

            progress_dialog.setLayout(progress_layout)
            progress_dialog.show()
            QApplication.processEvents()

            success, message = backup_all_tables_to_firebase()
            progress_dialog.close()

            result_msg = QMessageBox()
            if success:
                result_msg.setIcon(QMessageBox.Information)
                result_msg.setText("Backup Successful!")
                result_msg.setInformativeText(message)
            else:
                result_msg.setIcon(QMessageBox.Warning)
                result_msg.setText("Backup Failed!")
                result_msg.setInformativeText(message)
            result_msg.exec_()

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

            deleted_users = get_recently_deleted_users()
            for user in deleted_users:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(""))
                self.table.setItem(row, 1, QTableWidgetItem(user[0]))
                self.table.setItem(row, 2, QTableWidgetItem(""))
                self.table.setItem(row, 3, QTableWidgetItem(str(user[1])))
                self.table.setItem(row, 4, QTableWidgetItem("User"))

            deleted_posts = get_recently_deleted_posts()
            for post in deleted_posts:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(post[0])))
                self.table.setItem(row, 1, QTableWidgetItem(post[1]))
                self.table.setItem(row, 2, QTableWidgetItem(post[2]))
                self.table.setItem(row, 3, QTableWidgetItem(str(post[4])))
                self.table.setItem(row, 4, QTableWidgetItem("Post"))

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