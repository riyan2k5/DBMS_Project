from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database import register_user

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