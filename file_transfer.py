import socket
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
from tkinter.font import Font

class CustomStyle:
    PRIMARY = "#2C3E50"
    SECONDARY = "#3498DB"
    ACCENT = "#27AE60"
    WARNING = "#F39C12"
    ERROR = "#E74C3C"
    BG_GRADIENT_1 = "#2980B9"
    BG_GRADIENT_2 = "#6DD5FA"
    BG_GRADIENT_3 = "#FFFFFF"
    TEXT_LIGHT = "#ECF0F1"
    TEXT_DARK = "#2C3E50"

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1, color2, color3, **kwargs):
        super().__init__(parent, **kwargs)
        self._color1 = color1
        self._color2 = color2
        self._color3 = color3
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        for i in range(height):
            if i < height/2:
                ratio = 2.0 * i / height
                r = int(int(self._color1[1:3],  16) * (1-ratio) + int(self._color2[1:3],  16) * ratio)
                g = int(int(self._color1[3:5],  16) * (1-ratio) + int(self._color2[3:5],  16) * ratio)
                b = int(int(self._color1[5:7],  16) * (1-ratio) + int(self._color2[5:7],  16) * ratio)
            else:
                ratio = 2.0 * (i - height/2) / height
                r = int(int(self._color2[1:3],  16) * (1-ratio) + int(self._color3[1:3],  16) * ratio)
                g = int(int(self._color2[3:5],  16) * (1-ratio) + int(self._color3[3:5],  16) * ratio)
                b = int(int(self._color2[5:7],  16) * (1-ratio) + int(self._color3[5:7],  16) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")

class ModernButton(tk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(relief=tk.FLAT, bd=0, padx=20, pady=10,
                    font=('Helvetica', 10, 'bold'), cursor="hand2")
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)

    def _on_enter(self, e):
        self['background'] = CustomStyle.SECONDARY

    def _on_leave(self, e):
        self['background'] = CustomStyle.PRIMARY

class FileTransferClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Simultaneous File Transfer Client")
        self.root.geometry("600x700")
        self.background = GradientFrame(
            root, CustomStyle.BG_GRADIENT_1, CustomStyle.BG_GRADIENT_2, CustomStyle.BG_GRADIENT_3, highlightthickness=0
        )
        self.background.pack(fill="both", expand=True)

        main_container = tk.Frame(self.background, bg='white')
        main_container.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

        title_font = Font(family="Helvetica", size=16, weight="bold")
        tk.Label(main_container, text="File Transfer Client", font=title_font,
                 bg='white', fg=CustomStyle.PRIMARY).pack(pady=10)
        
        # Display local IP address
        self.local_ip = self.get_local_ip()
        ip_display_frame = tk.Frame(main_container, bg='white')
        ip_display_frame.pack(pady=5, fill="x", padx=20)
        tk.Label(ip_display_frame, text="Your IP Address:", bg='white',
                fg=CustomStyle.PRIMARY, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=(0,5))
        tk.Label(ip_display_frame, text=self.local_ip, bg=CustomStyle.PRIMARY, fg=CustomStyle.TEXT_LIGHT,
                font=("Helvetica", 9), padx=10, pady=3).pack(side=tk.LEFT)

        file_frame = tk.Frame(main_container, bg='white')
        file_frame.pack(pady=10, fill="x", padx=20)
        tk.Label(file_frame, text="File to Send:", bg='white',
                 fg=CustomStyle.PRIMARY, font=("Helvetica", 10, "bold")).pack(anchor="w")

        self.file_path = tk.StringVar()
        tk.Entry(file_frame, textvariable=self.file_path, width=50,
                 font=("Helvetica", 9), relief=tk.SOLID, bd=1).pack(side=tk.LEFT, pady=5, expand=True, fill="x")

        ModernButton(file_frame, text="Browse", command=self.browse_file,
                     bg=CustomStyle.PRIMARY, fg=CustomStyle.TEXT_LIGHT).pack(side=tk.RIGHT, padx=5)

        ip_frame = tk.Frame(main_container, bg='white')
        ip_frame.pack(pady=10, fill="x", padx=20)
        tk.Label(ip_frame, text="Target IP Addresses (one per line):", bg='white',
                 fg=CustomStyle.PRIMARY, font=("Helvetica", 10, "bold")).pack(anchor="w")

        text_frame = tk.Frame(main_container, bg='white')
        text_frame.pack(pady=5, fill="both", expand=True, padx=20)
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.ip_text = tk.Text(text_frame, height=5, width=50, yscrollcommand=scrollbar.set,
                               font=("Helvetica", 9), relief=tk.SOLID, bd=1)
        self.ip_text.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self.ip_text.yview)
        self.ip_text.insert(tk.END, "192.168.1.100\n192.168.1.101")

        button_frame = tk.Frame(main_container, bg='white')
        button_frame.pack(pady=20)
        ModernButton(button_frame, text="Send File", command=self.start_transfer,
                     bg=CustomStyle.PRIMARY, fg=CustomStyle.TEXT_LIGHT).pack()

        progress_frame = tk.Frame(main_container, bg='white')
        progress_frame.pack(pady=10, fill="both", expand=True, padx=20)
        tk.Label(progress_frame, text="Transfer Progress:", bg='white',
                 fg=CustomStyle.PRIMARY, font=("Helvetica", 10, "bold")).pack(anchor="w")

        canvas_frame = tk.Frame(progress_frame, bg='white')
        canvas_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        self.progress_frame = tk.Frame(self.canvas, bg='white')
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.progress_frame, anchor="nw")
        self.progress_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        tk.Label(main_container, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                 bg=CustomStyle.PRIMARY, fg=CustomStyle.TEXT_LIGHT, font=("Helvetica", 9)).pack(side=tk.BOTTOM, fill=tk.X)

    def get_local_ip(self):
        try:
            # Create a socket to determine the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Doesn't even have to be reachable
            s.connect(('8.8.8.8', 1))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"  # Return localhost if unable to determine IP

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_path.set(filename)
            self.status_var.set(f"Selected file: {os.path.basename(filename)}")

    def start_transfer(self):
        file_path = self.file_path.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid file")
            return

        ips = [ip.strip() for ip in self.ip_text.get("1.0", tk.END).split('\n') if ip.strip()]
        if not ips:
            messagebox.showerror("Error", "Please enter at least one IP address")
            return

        for widget in self.progress_frame.winfo_children():
            widget.destroy()

        self.status_var.set(f"Initiating transfers to {len(ips)} targets...")
        for ip in ips:
            ip_frame = tk.Frame(self.progress_frame, bg='white', pady=5)
            ip_frame.pack(fill="x", padx=5)
            header_frame = tk.Frame(ip_frame, bg='white')
            header_frame.pack(fill="x")
            progress_label = tk.Label(header_frame, text=f"Transfer to {ip}", bg='white',
                                      font=("Helvetica", 9, "bold"))
            progress_label.pack(side=tk.LEFT)
            status_label = tk.Label(header_frame, text="Connecting...", bg='white', fg=CustomStyle.WARNING)
            status_label.pack(side=tk.RIGHT)
            progress_bar = ttk.Progressbar(ip_frame, length=300, mode='determinate')
            progress_bar.pack(fill="x", pady=2)
            info_frame = tk.Frame(ip_frame, bg='white')
            info_frame.pack(fill="x")
            size_label = tk.Label(info_frame, text="0 KB / 0 KB", bg='white', font=("Helvetica", 8))
            size_label.pack(side=tk.LEFT)
            speed_label = tk.Label(info_frame, text="0 KB/s", bg='white', font=("Helvetica", 8))
            speed_label.pack(side=tk.RIGHT)
            threading.Thread(target=self.send_file,
                             args=(file_path, ip, progress_bar, status_label, size_label, speed_label),
                             daemon=True).start()

    def send_file(self, file_path, target_ip, progress_bar, status_label, size_label, speed_label, port=5000):
        try:
            status_label.config(text="Connecting...", fg=CustomStyle.WARNING)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            client_socket.connect((target_ip, port))
            status_label.config(text="Connected", fg=CustomStyle.SECONDARY)
            filename = os.path.basename(file_path)
            client_socket.send(filename.encode('utf-8'))
            if client_socket.recv(1024) != b'Filename received':
                raise Exception("Server did not acknowledge filename")
            file_size = os.path.getsize(file_path)
            client_socket.send(str(file_size).encode('utf-8'))
            if client_socket.recv(1024) != b'File size received':
                raise Exception("Server did not acknowledge file size")
            status_label.config(text="Transferring...", fg=CustomStyle.SECONDARY)
            sent_bytes = 0
            start_time = time.time()
            last_update_time = start_time
            last_update_bytes = 0
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(4096)
                    if not chunk:
                        break
                    client_socket.send(chunk)
                    sent_bytes += len(chunk)
                    progress = int((sent_bytes / file_size) * 100)
                    progress_bar['value'] = progress
                    size_label.config(text=f"{sent_bytes/1024:.1f} KB / {file_size/1024:.1f} KB")
                    current_time = time.time()
                    if current_time - last_update_time >= 0.5:
                        speed = (sent_bytes - last_update_bytes) / (current_time - last_update_time) / 1024
                        speed_label.config(text=f"{speed:.1f} KB/s")
                        last_update_time = current_time
                        last_update_bytes = sent_bytes
                    self.root.update_idletasks()
            client_socket.close()
            status_label.config(text="Completed", fg=CustomStyle.ACCENT)
            speed_label.config(text="Done")
        except Exception as e:
            status_label.config(text="Failed", fg=CustomStyle.ERROR)
            size_label.config(text=str(e)[:20])

class FileReceiveServer:
    def __init__(self, host='0.0.0.0', port=5000, save_directory='received_files'):
        self.save_directory = save_directory
        os.makedirs(save_directory, exist_ok=True)
        self.host = host
        self.port = port
        self.root = None
        self.log_text = None
        self.local_ip = self.get_local_ip()
        try:
            self.setup_gui()
        except:
            print("Running in console mode")

    def get_local_ip(self):
        try:
            # Create a socket to determine the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Doesn't even have to be reachable
            s.connect(('8.8.8.8', 1))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"  # Return localhost if unable to determine IP

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("File Transfer Server")
        self.root.geometry("700x600")
        self.background = GradientFrame(
            self.root, CustomStyle.BG_GRADIENT_1, CustomStyle.BG_GRADIENT_2, CustomStyle.BG_GRADIENT_3, highlightthickness=0
        )
        self.background.pack(fill="both", expand=True)
        main_container = tk.Frame(self.background, bg='white')
        main_container.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        title_font = Font(family="Helvetica", size=16, weight="bold")
        tk.Label(main_container, text="File Transfer Server", font=title_font,
                 bg='white', fg=CustomStyle.PRIMARY).pack(pady=10)
                 
        # Display local IP address
        ip_display_frame = tk.Frame(main_container, bg='white')
        ip_display_frame.pack(pady=5, fill="x", padx=20)
        tk.Label(ip_display_frame, text="Server IP Address:", bg='white',
                fg=CustomStyle.PRIMARY, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=(0,5))
        tk.Label(ip_display_frame, text=self.local_ip, bg=CustomStyle.PRIMARY, fg=CustomStyle.TEXT_LIGHT,
                font=("Helvetica", 9), padx=10, pady=3).pack(side=tk.LEFT)
        
        info_frame = tk.Frame(main_container, bg='white')
        info_frame.pack(pady=10, padx=20, fill="x")
        tk.Label(info_frame, text=f"Server listening on port {self.port}",
                 bg='white', fg=CustomStyle.PRIMARY, font=("Helvetica", 12, "bold")).pack(side=tk.LEFT)
                 
        # Save directory information
        save_dir_frame = tk.Frame(main_container, bg='white')
        save_dir_frame.pack(pady=5, fill="x", padx=20)
        tk.Label(save_dir_frame, text="Save Directory:", bg='white',
                fg=CustomStyle.PRIMARY, font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=(0,5))
        tk.Label(save_dir_frame, text=os.path.abspath(self.save_directory),
                bg='white', fg=CustomStyle.SECONDARY, font=("Helvetica", 9)).pack(side=tk.LEFT)
                
        log_frame = tk.Frame(main_container, bg='white')
        log_frame.pack(pady=20, padx=20, fill="both", expand=True)
        tk.Label(log_frame, text="Transfer Log:", bg='white',
                 fg=CustomStyle.PRIMARY, font=("Helvetica", 10, "bold")).pack(anchor="w")
        log_container = tk.Frame(log_frame, bg='white')
        log_container.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(log_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text = tk.Text(log_container, height=15, width=70, yscrollcommand=scrollbar.set,
                                font=("Helvetica", 9), bg='white', relief=tk.SOLID, bd=1)
        self.log_text.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)
        self.log_text.config(state=tk.DISABLED)
        self.status_var = tk.StringVar()
        self.status_var.set("Server ready")
        tk.Label(main_container, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                 bg=CustomStyle.PRIMARY, fg=CustomStyle.TEXT_LIGHT, font=("Helvetica", 9)).pack(side=tk.BOTTOM, fill=tk.X)

    def log(self, message):
        print(message)
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
            if self.status_var:
                self.status_var.set(message)

    def start_server(self):
        server_thread = threading.Thread(target=self.server_loop)
        server_thread.daemon = True
        server_thread.start()
        if self.root:
            self.log("Server started. Waiting for connections...")
            self.root.mainloop()
        else:
            self.log("Server started. Waiting for connections...")
            server_thread.join()

    def server_loop(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            self.log(f"Server listening on {self.host}:{self.port}")
            while True:
                client_socket, address = server_socket.accept()
                self.log(f"Connection from {address[0]}:{address[1]}")
                threading.Thread(target=self.receive_file, args=(client_socket, address), daemon=True).start()
        except Exception as e:
            self.log(f"Server error: {str(e)}")

    def receive_file(self, client_socket, address):
        try:
            filename = client_socket.recv(1024).decode('utf-8')
            self.log(f"Receiving file '{filename}' from {address[0]}")
            client_socket.send(b'Filename received')
            file_size = int(client_socket.recv(1024).decode('utf-8'))
            self.log(f"File size: {file_size/1024:.1f} KB")
            client_socket.send(b'File size received')
            full_path = os.path.join(self.save_directory, filename)
            received_bytes = 0
            start_time = time.time()
            with open(full_path, 'wb') as file:
                while received_bytes < file_size:
                    chunk = client_socket.recv(4096)
                    if not chunk:
                        break
                    file.write(chunk)
                    received_bytes += len(chunk)
                    if received_bytes % (512 * 1024) == 0:
                        percent = (received_bytes / file_size) * 100
                        self.log(f"Transfer progress: {percent:.1f}% ({received_bytes/1024:.1f} KB)")
            elapsed_time = time.time() - start_time
            speed = file_size / (1024 * elapsed_time) if elapsed_time > 0 else 0
            self.log(f"File '{filename}' received successfully from {address[0]}")
            self.log(f"Transfer complete: {file_size/1024:.1f} KB in {elapsed_time:.1f} seconds ({speed:.1f} KB/s)")
            self.log(f"File saved to {full_path}")
            client_socket.close()
        except Exception as e:
            self.log(f"Error receiving file from {address[0]}: {str(e)}")

class StartupSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer System")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Create gradient background
        self.background = GradientFrame(
            root, CustomStyle.BG_GRADIENT_1, CustomStyle.BG_GRADIENT_2, CustomStyle.BG_GRADIENT_3, highlightthickness=0
        )
        self.background.pack(fill="both", expand=True)

        # Main container
        main_container = tk.Frame(self.background, bg='white')
        main_container.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

        # Title
        title_font = Font(family="Helvetica", size=18, weight="bold")
        tk.Label(main_container, text="Simultaneous File Transfer System", font=title_font,
                bg='white', fg=CustomStyle.PRIMARY).pack(pady=30)

        # Local IP display
        self.local_ip = self.get_local_ip()
        ip_frame = tk.Frame(main_container, bg='white')
        ip_frame.pack(pady=15)
        tk.Label(ip_frame, text="Your IP Address:", bg='white',
                fg=CustomStyle.PRIMARY, font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=(0,10))
        ip_label = tk.Label(ip_frame, text=self.local_ip, bg=CustomStyle.PRIMARY, fg=CustomStyle.TEXT_LIGHT,
                font=("Helvetica", 11), padx=15, pady=5)
        ip_label.pack(side=tk.LEFT)

        # Mode selection title
        tk.Label(main_container, text="Select Operation Mode", font=("Helvetica", 12, "bold"),
                bg='white', fg=CustomStyle.PRIMARY).pack(pady=(30, 15))

        # Buttons frame
        buttons_frame = tk.Frame(main_container, bg='white')
        buttons_frame.pack(pady=10)

        # Client button
        client_button = tk.Frame(buttons_frame, bg=CustomStyle.SECONDARY, padx=5, pady=5, cursor="hand2")
        client_button.pack(side=tk.LEFT, padx=20)
        client_button.bind("<Button-1>", self.start_client)
        client_button.bind("<Enter>", lambda e: client_button.config(bg=CustomStyle.ACCENT))
        client_button.bind("<Leave>", lambda e: client_button.config(bg=CustomStyle.SECONDARY))

        client_icon = tk.Label(client_button, text="📤", font=("Helvetica", 24), 
                              bg=CustomStyle.SECONDARY, fg="white")
        client_icon.pack(pady=(10, 5))
        client_icon.bind("<Button-1>", self.start_client)
        client_icon.bind("<Enter>", lambda e: client_button.config(bg=CustomStyle.ACCENT))
        client_icon.bind("<Leave>", lambda e: client_button.config(bg=CustomStyle.SECONDARY))

        client_label = tk.Label(client_button, text="Client Mode", font=("Helvetica", 12, "bold"),
                              bg=CustomStyle.SECONDARY, fg="white", padx=15, pady=5)
        client_label.pack()
        client_label.bind("<Button-1>", self.start_client)
        client_label.bind("<Enter>", lambda e: client_button.config(bg=CustomStyle.ACCENT))
        client_label.bind("<Leave>", lambda e: client_button.config(bg=CustomStyle.SECONDARY))

        # Server button
        server_button = tk.Frame(buttons_frame, bg=CustomStyle.PRIMARY, padx=5, pady=5, cursor="hand2")
        server_button.pack(side=tk.LEFT, padx=20)
        server_button.bind("<Button-1>", self.start_server)
        server_button.bind("<Enter>", lambda e: server_button.config(bg=CustomStyle.SECONDARY))
        server_button.bind("<Leave>", lambda e: server_button.config(bg=CustomStyle.PRIMARY))

        server_icon = tk.Label(server_button, text="📥", font=("Helvetica", 24), 
                              bg=CustomStyle.PRIMARY, fg="white")
        server_icon.pack(pady=(10, 5))
        server_icon.bind("<Button-1>", self.start_server)
        server_icon.bind("<Enter>", lambda e: server_button.config(bg=CustomStyle.SECONDARY))
        server_icon.bind("<Leave>", lambda e: server_button.config(bg=CustomStyle.PRIMARY))

        server_label = tk.Label(server_button, text="Server Mode", font=("Helvetica", 12, "bold"),
                              bg=CustomStyle.PRIMARY, fg="white", padx=15, pady=5)
        server_label.pack()
        server_label.bind("<Button-1>", self.start_server)
        server_label.bind("<Enter>", lambda e: server_button.config(bg=CustomStyle.SECONDARY))
        server_label.bind("<Leave>", lambda e: server_button.config(bg=CustomStyle.PRIMARY))

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to start")
        tk.Label(main_container, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                bg=CustomStyle.PRIMARY, fg=CustomStyle.TEXT_LIGHT, font=("Helvetica", 9)).pack(side=tk.BOTTOM, fill=tk.X)

    def get_local_ip(self):
        try:
            # Create a socket to determine the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Doesn't even have to be reachable
            s.connect(('8.8.8.8', 1))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"  # Return localhost if unable to determine IP

    def start_client(self, event=None):
        self.status_var.set("Starting client...")
        self.root.destroy()
        root = tk.Tk()
        app = FileTransferClient(root)
        root.mainloop()

    def start_server(self, event=None):
        self.status_var.set("Starting server...")
        self.root.destroy()
        save_dir = 'received_files'  # Default save directory
        server = FileReceiveServer(save_directory=save_dir)
        server.start_server()

def main():
    root = tk.Tk()
    app = StartupSelector(root)
    root.mainloop()

if __name__ == '__main__':
    main()
