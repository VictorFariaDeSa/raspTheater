import cv2
import tkinter as tk
from PIL import Image, ImageTk
import threading
import socketio
import time

# Variável global para armazenar a instância do player
video_player = None

class VideoPlayer:
    def __init__(self, root, video_path):
        global video_player
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.video_path = video_path

        # Definição das dimensões da tela
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Criar label para exibir o vídeo
        self.label = tk.Label(self.root)
        self.label.pack(expand=True, fill="both")

        # Ocultação do cursor do mouse
        self.root.config(cursor="none")

        self.cap = cv2.VideoCapture(self.video_path)
        self.update_frame()

        # Atualiza a variável global com a instância do player
        video_player = self

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (self.screen_width, self.screen_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(img)
            self.label.config(image=img)
            self.label.image = img
            self.root.after(30, self.update_frame)  # Atualiza a cada 30ms
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reinicia o vídeo quando chega ao final

    def load_video(self, video_path):
        """ Carrega um novo vídeo e reinicia a reprodução """
        if self.cap.isOpened():
            self.cap.release()  # Fecha o vídeo atual antes de abrir o novo
        self.cap = cv2.VideoCapture(video_path)  # Carrega o novo vídeo
        if not self.cap.isOpened():
            print(f"Erro ao abrir o vídeo: {video_path}")
            return
        self.video_path = video_path
        self.update_frame()  # Inicia a reprodução do novo vídeo

    def change_video(self, new_video_path):
        """ Troca o vídeo em tempo real """
        print(f"Trocando vídeo para: {new_video_path}")
        self.load_video(new_video_path)

    def exit_fullscreen(self, event=None):
        self.cap.release()
        self.root.destroy()

def start_tkinter():
    """ Executa o Tkinter na thread principal """
    global video_player
    root = tk.Tk()
    video_player = VideoPlayer(root, "video.mp4")  # Define o player
    root.mainloop()

def start_socketio():
    """ Conecta ao servidor SocketIO em uma thread separada """
    sio = socketio.Client()

    @sio.on("change_video")
    def on_update_video(data):
        global video_player
        if video_player:
            video_player.change_video(data)
        else:
            print("Erro: VideoPlayer ainda não foi inicializado.")

    sio.connect("http://127.0.0.1:5000")
    sio.emit("client_message", {"message": "Olá, servidor!"})
    sio.wait()  # Espera por novos eventos

# Criar thread para o Tkinter
tk_thread = threading.Thread(target=start_tkinter, daemon=True)
tk_thread.start()

# Criar thread para o SocketIO
socketio_thread = threading.Thread(target=start_socketio, daemon=True)
socketio_thread.start()

# Aguardar indefinidamente para manter as threads ativas
while True:
    time.sleep(1)
