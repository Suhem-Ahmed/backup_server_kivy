import os
import paramiko
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window


class SSHFileUploader(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.spacing = 10  # Add spacing between widgets

        # Set background color and center layout
        self.background_color = (0, 0, 0, 1)  # Black background color
        self.center_layout()

        # SSH Server Details
        self.hostname_label = Label(text='Hostname/IP:', size_hint=(1, None), height=30, color=(1, 1, 1, 1))
        self.add_widget(self.hostname_label)
        self.hostname_input = TextInput(multiline=False, size_hint=(1, None), height=30)
        self.add_widget(self.hostname_input)

        self.username_label = Label(text='Username:', size_hint=(1, None), height=30, color=(1, 1, 1, 1))
        self.add_widget(self.username_label)
        self.username_input = TextInput(multiline=False, size_hint=(1, None), height=30)
        self.add_widget(self.username_input)

        self.password_label = Label(text='Password:', size_hint=(1, None), height=30, color=(1, 1, 1, 1))
        self.add_widget(self.password_label)
        self.password_input = TextInput(password=True, multiline=False, size_hint=(1, None), height=30)
        self.add_widget(self.password_input)

        # File chooser
        self.file_chooser = FileChooserListView(path='.', size_hint=(1, 0.5))
        self.add_widget(self.file_chooser)

        # Upload Button
        self.upload_button = Button(text='Upload', size_hint=(1, None), height=40)
        self.upload_button.bind(on_press=self.upload_files)
        self.add_widget(self.upload_button)

    def center_layout(self):
        # Center the layout within the window
        self.size_hint = (None, None)
        self.width = 300
        self.height = 400  # Adjust height as needed
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        Window.clearcolor = (0, 0, 0, 1)  # Black background color

    def upload_files(self, instance):
        hostname = self.hostname_input.text
        username = self.username_input.text
        password = self.password_input.text
        selected_files = self.file_chooser.selection

        if not all([hostname, username, password, selected_files]):
            # Handle error if any field is empty
            self.show_popup("Error", "Please fill in all fields and select files to upload.")
            return

        try:
            # Create an SSH client instance
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the SSH server
            client.connect(hostname, port=22, username=username, password=password)

            # Open an SFTP session on the SSH server
            sftp = client.open_sftp()

            # Upload selected files
            for file_path in selected_files:
                remote_file = os.path.join('/home', username, 'server', os.path.basename(file_path))
                sftp.put(file_path, remote_file)
                print(f"Uploaded {file_path} to {hostname}:{remote_file}")

            # Close the SSH and SFTP sessions
            sftp.close()
            client.close()

            self.show_popup("Success", "Files uploaded successfully.")
        except Exception as e:
            self.show_popup("Error", f"Upload failed: {e}")

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()


class SSHFileUploaderApp(App):
    def build(self):
        return SSHFileUploader()


if __name__ == '__main__':
    SSHFileUploaderApp().run()
