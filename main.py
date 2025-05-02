import psycopg2
from psycopg2 import sql, errors
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QStackedWidget)

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
                # Use sql.SQL and sql.Identifier to safely insert identifiers
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
                query = sql.SQL("SELECT * FROM users WHERE username = %s AND password = %s")
                cur.execute(query, (username, password))
                user = cur.fetchone()
                if user:
                    return True, "Login successful"
                else:
                    return False, "Invalid username or password"
    except errors.DatabaseError as e:
        return False, f"Database error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


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

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        success, message = check_credentials(username, password)

        msg = QMessageBox()
        if success:
            msg.setIcon(QMessageBox.Information)
            msg.setText(message)
            msg.exec_()
            # Here you would typically proceed to the main application
            # For example: self.stacked_widget.setCurrentIndex(2)
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText(message)
            msg.exec_()

    def switch_to_register(self):
        self.stacked_widget.setCurrentIndex(0)
        self.username_input.clear()
        self.password_input.clear()


class MainApp(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        welcome_label = QLabel("Welcome to the Application!")
        layout.addWidget(welcome_label)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication([])

    # Create a stacked widget to handle multiple screens
    stacked_widget = QStackedWidget()

    # Create and add the registration and login screens
    registration_app = RegistrationApp(stacked_widget)
    login_app = LoginApp(stacked_widget)
    main_app = MainApp(stacked_widget)  # This would be the main application after login

    stacked_widget.addWidget(registration_app)
    stacked_widget.addWidget(login_app)
    stacked_widget.addWidget(main_app)

    stacked_widget.setCurrentIndex(1)  # Start with login screen
    stacked_widget.setWindowTitle('User Authentication')
    stacked_widget.setFixedSize(300, 250)
    stacked_widget.show()

    app.exec_()