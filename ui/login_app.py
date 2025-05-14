from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database import check_credentials, check_admin_credentials

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

        if check_admin_credentials(username, password):
            self.stacked_widget.setCurrentIndex(3)
            self.username_input.clear()
            self.password_input.clear()
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