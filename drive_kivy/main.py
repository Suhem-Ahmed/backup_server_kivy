# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.graphics import Color
import paramiko
from paramiko import SSHClient
from paramiko.sftp_client import SFTPClient


class FileTransferApp(App):
    def build(self):
        self.sftp = None

        self.server_address_input = TextInput(hint_text="Server Address", size_hint_y=None, height=40)
        self.username_input = TextInput(hint_text="Username", size_hint_y=None, height=40)
        self.password_input = TextInput(hint_text="Password", password=True, size_hint_y=None, height=40)
        self.path_on_server_input = TextInput(hint_text="Path on Server", size_hint_y=None, height=40)
        
        self.file_chooser = FileChooserListView()
        self.status_label = Label(text="Select a file to upload", size_hint_y=None, height=40)
        self.upload_button = Button(text="Upload", size_hint_y=None, height=50)
        self.upload_button.bind(on_press=self.upload_file)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="SFTP File Uploader", font_size=30, size_hint_y=None, height=50, color=(0, 0.7, 1, 1)))
        layout.add_widget(self.server_address_input)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.path_on_server_input)
        layout.add_widget(self.file_chooser)
        layout.add_widget(self.status_label)
        layout.add_widget(self.upload_button)
        
        with layout.canvas.before:
            Color(0.1, 0.9, 0.5, 0.1)  # Background color
            layout.rect = Window.size
        
        return layout

    def connect_to_server(self):
        host = self.server_address_input.text.strip()
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(host, port=22, username=username, password=password)
            self.sftp = client.open_sftp()
        except paramiko.ssh_exception.AuthenticationException:
            self.show_popup("Authentication Error", "Invalid username or password.")
        except Exception as e:
            self.show_popup("Connection Error", f"Failed to connect to server: {e}")
    
    def upload_file(self, instance):
        if not self.sftp:
            self.connect_to_server()
            if not self.sftp:
                return
        
        selected_file = self.file_chooser.selection and self.file_chooser.selection[0] or None
        path_on_server = self.path_on_server_input.text.strip()
        
        if selected_file:
            try:
                self.sftp.put(selected_file, f"{path_on_server}/{selected_file.split('/')[-1]}")
                self.status_label.text = f"File '{selected_file.split('/')[-1]}' uploaded successfully!"
            except Exception as e:
                self.show_popup("Upload Error", f"Failed to upload file: {e}")
        else:
            self.status_label.text = "Please select a file to upload"
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()


if __name__ == '__main__':
    Window.size = (600, 600)
    FileTransferApp().run()
