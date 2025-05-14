from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit,
                             QPushButton, QListWidget, QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt
from database import get_user_conversations, get_conversation, send_message

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

        self.conversation_list = QListWidget()
        self.conversation_list.itemClicked.connect(self.open_conversation)
        layout.addWidget(self.conversation_list, 1)

        right_panel = QVBoxLayout()

        self.conversation_header = QLabel("Select a conversation")
        right_panel.addWidget(self.conversation_header)

        self.messages_display = QTextEdit()
        self.messages_display.setReadOnly(True)
        right_panel.addWidget(self.messages_display, 1)

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
        for i in range(self.conversation_list.count()):
            item = self.conversation_list.item(i)
            if item.text().startswith(username):
                self.conversation_list.setCurrentItem(item)
                self.open_conversation(item)
                return

        self.current_conversation = username
        self.update_conversation_view()

    def open_conversation(self, item):
        other_user = item.text().split()[0]
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