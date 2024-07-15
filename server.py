
import socket
import threading
import pickle

# Kullanıcı mesaj kayıtlarını ve bağlantılarını tutmak için veri yapıları
user_messages = {}  # Kullanıcı adlarına göre mesajlar
user_connections = {}  # Kullanıcı adlarına göre bağlantılar

def handle_client(client_socket, addr, username):
    # İstemciye bağlı kalınana kadar mesajları işle
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break

            # Alınan mesajı işleme
            data = pickle.loads(message)
            if data['type'] == 'message':
                save_message(username, data['message'])  # Mesajı kaydet
                broadcast_message(username, data['message'])  # Mesajı diğer kullanıcılara yayınla
        except ConnectionResetError:
            break

    # İstemci bağlantısını kapat ve kullanıcıyı bağlantı listesinden kaldır
    client_socket.close()
    remove_client(username)
    print(f"[DISCONNECTED] {username} disconnected")

def save_message(username, message):
    # Kullanıcıya ait mesajları kaydetmek için
    if username not in user_messages:
        user_messages[username] = []
    user_messages[username].append(message)

def broadcast_message(username, message):
    # Kullanıcının gönderdiği mesajı diğer kullanıcılara yayınlamak için
    for user, conn in user_connections.items():
        if user != username:
            conn.send(pickle.dumps({'type': 'message', 'username': username, 'message': message}))

def remove_client(username):
    # Kullanıcıyı bağlantı listesinden kaldırmak için
    if username in user_connections:
        del user_connections[username]

def start_server():
    # Sunucuyu başlatmak ve bağlantıları dinlemek için
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(5)
    print("[STARTED] Server started and listening on port 5555")

    while True:
        # Yeni bir istemci bağlantısı kabul et
        client_socket, addr = server.accept()
        username = client_socket.recv(1024).decode('utf-8')
        user_connections[username] = client_socket
        print(f"[CONNECTED] {username} connected from {addr}")

        # İstemciye ayrı bir iş parçacığında hizmet vermek için bir iş parçacığı başlat
        thread = threading.Thread(target=handle_client, args=(client_socket, addr, username))
        thread.start()

if __name__ == "__main__":
    start_server()
