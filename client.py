
#ÖNCE SERVERI ÇALIŞTIRINIZ


import sys
import socket
import threading
import pickle
from PyQt5 import QtWidgets, QtCore


class Client(QtWidgets.QWidget):
    def __init__(self, host, port, username):
        super().__init__()

        # Bağlantı oluşturma ve kullanıcı adını sunucuya gönderme
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.client_socket.send(username.encode('utf-8'))

        # Kullanıcı adı ve mesajlar listesi
        self.username = username
        self.messages = []

        # Kullanıcı listesi ve gruplar
        self.user_list = {"Arkadaşlarım": [], "Ailem": [], "Diğer": []}

        # Arayüzü başlatma
        self.init_ui()

        # Mesajları almak için arka planda bir thread başlatma
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def init_ui(self):
        # Arayüzü başlatma ve ayarlar
        self.setWindowTitle("Chat Application")
        self.layout = QtWidgets.QVBoxLayout()

        # Sohbet görüntüleyici
        self.chat_display = QtWidgets.QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        # Mesaj girişi
        self.message_input = QtWidgets.QLineEdit()
        self.layout.addWidget(self.message_input)

        # Mesaj gönderme düğmesi
        self.send_button = QtWidgets.QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        # Geçmişi görüntüleme düğmesi
        self.history_button = QtWidgets.QPushButton("Show History")
        self.history_button.clicked.connect(self.show_history)
        self.layout.addWidget(self.history_button)

        # Mesajlarda arama yapma girişi
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search messages...")
        self.layout.addWidget(self.search_input)

        # Mesajlarda arama yapma düğmesi
        self.search_button = QtWidgets.QPushButton("Search")
        self.search_button.clicked.connect(self.search_messages)
        self.layout.addWidget(self.search_button)

        # Gruplar için açılır menü
        self.group_combobox = QtWidgets.QComboBox()
        self.group_combobox.addItems(self.user_list.keys())
        self.group_combobox.currentTextChanged.connect(self.update_user_list)
        self.layout.addWidget(self.group_combobox)

        # Kullanıcı listesi için widget
        self.user_list_widget = QtWidgets.QListWidget()
        self.layout.addWidget(self.user_list_widget)

        # Kullanıcıyı gruba ekleme düğmesi
        self.add_user_button = QtWidgets.QPushButton("Add User to Group")
        self.add_user_button.clicked.connect(self.add_user_to_group)
        self.layout.addWidget(self.add_user_button)

        # Arayüzü ayarlama
        self.setLayout(self.layout)
        self.show()

    def send_message(self):
        # Mesaj gönderme
        message = self.message_input.text()
        if message:
            data = {'type': 'message', 'message': message}
            self.client_socket.send(pickle.dumps(data))
            self.message_input.clear()
            self.chat_display.append(f"Me: {message}")
            self.messages.append(message)

    def receive_messages(self):
        # Mesajları alma
        while True:
            try:
                message = self.client_socket.recv(1024)
                if message:
                    data = pickle.loads(message)
                    if data['type'] == 'message':
                        self.chat_display.append(f"{data['username']}: {data['message']}")
                        self.messages.append(data['message'])
                    elif data['type'] == 'user_list':
                        self.user_list = data['user_list']
                        self.update_user_list()
            except ConnectionResetError:
                break

    def show_history(self):
        # Geçmişi görüntüleme
        self.chat_display.clear()
        for message in self.messages:
            self.chat_display.append(message)

    def search_messages(self):
        # Mesajlarda arama yapma
        search_term = self.search_input.text()
        self.chat_display.clear()
        for message in self.messages:
            if search_term in message:
                self.chat_display.append(message)

    def update_user_list(self):
        # Kullanıcı listesini güncelleme
        current_group = self.group_combobox.currentText()
        self.user_list_widget.clear()
        for user in self.user_list[current_group]:
            self.user_list_widget.addItem(user)

    def add_user_to_group(self):
        # Kullanıcıyı gruba ekleme
        user, ok = QtWidgets.QInputDialog.getText(self, "Add User to Group", "Enter username:")
        if ok:
            group, ok = QtWidgets.QInputDialog.getItem(self, "Select Group", "Select group:", self.user_list.keys(), 0,
                                                       False)
            if ok:
                self.user_list[group].append(user)
                self.update_user_list()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    username = input("Enter your username: ")
    client = Client('127.0.0.1', 5555, username)
    sys.exit(app.exec_())
