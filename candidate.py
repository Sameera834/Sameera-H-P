import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from socketio import Client

class VideoSenderThread(QThread):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.capture = cv2.VideoCapture(0)
        self.running = True

    def run(self):
        while self.running:
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = buffer.tobytes()
                self.socket.emit('video_frame', frame_data)
                cv2.waitKey(100)

    def stop(self):
        self.running = False
        self.capture.release()

class VideoReceiverThread(QThread):
    frame_signal = pyqtSignal(bytes)

    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.running = True

    def run(self):
        self.socket.on('video_frame', self.emit_frame)

    def emit_frame(self, frame_data):
        self.frame_signal.emit(frame_data)

    def stop(self):
        self.running = False

class CandidateClient(QWidget):
    def __init__(self, candidate_id):
        super().__init__()
        self.candidate_id = candidate_id
        self.initUI()
        self.socket = Client()
        self.socket.connect('http://127.0.0.1:5000')
        self.socket.on('chat_message', self.receive_message)
        self.socket.emit('new_candidate', self.candidate_id)

        self.video_sender_thread = VideoSenderThread(self.socket)
        self.video_sender_thread.start()

        self.video_receiver_thread = VideoReceiverThread(self.socket)
        self.video_receiver_thread.frame_signal.connect(self.update_video_frame)
        self.video_receiver_thread.start()

    def initUI(self):
        self.setWindowTitle(f'Candidate {self.candidate_id} Chat')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.video_label = QLabel()
        self.layout.addWidget(self.video_label)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.layout.addWidget(self.text_area)

        self.message_input = QLineEdit()
        self.layout.addWidget(self.message_input)

        self.send_button = QPushButton('Send Message')
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

    def update_video_frame(self, frame_data):
        np_data = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))

    def receive_message(self, data):
        # Display message only if it's not from the candidate
        if data['sender'] != self.candidate_id:
            self.text_area.append(f"{data['sender']}: {data['message']}")

    def send_message(self):
        message = self.message_input.text().strip()  # Remove leading/trailing whitespace
        if message:  # Only send if the message is not empty
            self.text_area.append(f"{self.candidate_id}: {message}")
            self.socket.emit('chat_message', {'sender': self.candidate_id, 'message': message})
            self.message_input.clear()

    def keyPressEvent(self, event):
        if event.key() == 16777220:  # Enter key
            self.send_message()

    def closeEvent(self, event):
        self.video_sender_thread.stop()
        self.video_receiver_thread.stop()
        self.socket.disconnect()

if __name__ == "__main__":
    candidate_id = sys.argv[1] if len(sys.argv) > 1 else 'candidate1'
    app = QApplication(sys.argv)
    client = CandidateClient(candidate_id)
    client.show()
    sys.exit(app.exec_())