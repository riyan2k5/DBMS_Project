from PyQt5.QtWidgets import QApplication, QStackedWidget
from ui import RegistrationApp, LoginApp, MainApp, AdminApp

if __name__ == '__main__':
    app = QApplication([])
    stacked_widget = QStackedWidget()

    registration_app = RegistrationApp(stacked_widget)
    login_app = LoginApp(stacked_widget)
    main_app = MainApp(stacked_widget)
    admin_app = AdminApp(stacked_widget)

    stacked_widget.addWidget(registration_app)
    stacked_widget.addWidget(login_app)
    stacked_widget.addWidget(main_app)
    stacked_widget.addWidget(admin_app)

    stacked_widget.setCurrentIndex(1)
    stacked_widget.setWindowTitle('Social Media App')
    stacked_widget.setFixedSize(500, 400)
    stacked_widget.show()

    app.exec_()