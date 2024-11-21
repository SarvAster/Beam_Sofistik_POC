import sys
import os
import threading
import configparser
from flamb import Iteration
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QDialog, QFormLayout
)

class ConfigurationDialog(QDialog):
    def __init__(self, current_sofistik_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.sofistik_path = current_sofistik_path
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # minimal margins
        layout.setSpacing(5)  # minimal spacing

        self.sofistik_path_edit = QLineEdit(self.sofistik_path)
        browse_button = QPushButton("Browse")
        browse_button.setMinimumWidth(60)
        browse_button.clicked.connect(self.browse_sofistik)

        sofistik_layout = QHBoxLayout()
        sofistik_layout.setContentsMargins(0, 0, 0, 0)
        sofistik_layout.setSpacing(5)
        sofistik_layout.addWidget(self.sofistik_path_edit)
        sofistik_layout.addWidget(browse_button)

        layout.addRow(QLabel("SOFiSTiK Installation Path:"), sofistik_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)

        layout.addRow(buttons_layout)
        self.setLayout(layout)

    def browse_sofistik(self):
        directory = QFileDialog.getExistingDirectory(self, "Select SOFiSTiK Installation Directory")
        if directory:
            self.sofistik_path_edit.setText(directory)

    def accept(self):
        self.sofistik_path = self.sofistik_path_edit.text()
        if not os.path.isdir(self.sofistik_path):
            QMessageBox.critical(self, "Input Error", "Please select a valid directory.")
            return
        super().accept()

class StreamToTextEdit(QObject):
    text_written = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def write(self, message):
        # Emit signal for each line
        for line in message.splitlines():
            self.text_written.emit(line.strip())

    def flush(self):
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SOFiSTiK Processor")
        self.setGeometry(100, 100, 600, 600)
        self.sofistik_path = self.load_sofistik_path()
        self.setup_ui()

        # Redirect stdout and stderr to the output_text
        self.stdout_stream = StreamToTextEdit(self)
        self.stdout_stream.text_written.connect(self.append_output_text)
        sys.stdout = self.stdout_stream
        sys.stderr = self.stdout_stream

    def load_sofistik_path(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if 'SOFiSTiK' in config and 'sofistik_path' in config['SOFiSTiK']:
            path = config['SOFiSTiK']['sofistik_path']
            return os.path.abspath(os.path.normpath(path))
        else:
            QMessageBox.warning(self, "Configuration Warning", "SOFiSTiK path not found. Please set it via the Configuration dialog.")
            return ""

    def setup_ui(self):
        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Configuration button at the top
        self.config_button = QPushButton("Configuration")
        self.config_button.clicked.connect(self.open_configuration_dialog)
        main_layout.addWidget(self.config_button, alignment=Qt.AlignLeft)

        # File selection
        file_layout = QHBoxLayout()
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(5)
        file_label = QLabel("Select .dat File:")
        self.file_entry = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.setFixedWidth(60)
        browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_entry, stretch=1)
        file_layout.addWidget(browse_button)
        main_layout.addLayout(file_layout)

        # Input fields layout
        input_form_layout = QFormLayout()
        input_form_layout.setContentsMargins(0, 0, 0, 0)
        input_form_layout.setSpacing(5)

        # H input
        self.h_entry = QLineEdit()
        input_form_layout.addRow(QLabel("Enter H:"), self.h_entry)

        # V input
        self.v_entry = QLineEdit()
        input_form_layout.addRow(QLabel("Enter V:"), self.v_entry)

        # Epsilon input
        self.epsilon_entry = QLineEdit()
        input_form_layout.addRow(QLabel("Enter epsilon:"), self.epsilon_entry)

        main_layout.addLayout(input_form_layout)

        # Run button
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_process)
        main_layout.addWidget(self.run_button, alignment=Qt.AlignLeft)

        # Output display
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        font_metrics = self.output_text.fontMetrics()
        line_height = font_metrics.lineSpacing()
        desired_lines = 25
        self.output_text.setFixedHeight(line_height * desired_lines + 10)
        main_layout.addWidget(self.output_text)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select .dat File", "", "DAT Files (*.dat)")
        if file_path:
            self.file_entry.setText(file_path)
            print(f".dat file path set to: {file_path}")

    def run_process(self):
        # Clear previous output
        self.output_text.clear()

        # Get user inputs
        dat_file = self.file_entry.text()
        H = self.h_entry.text()
        V = self.v_entry.text()
        epsilon = self.epsilon_entry.text()

        # Validate inputs
        if not os.path.isfile(dat_file):
            print("Error: Invalid .dat file path.")
            QMessageBox.critical(self, "Input Error", "Please select a valid .dat file.")
            return

        if not self.sofistik_path:
            print("Error: SOFiSTiK path is not set.")
            QMessageBox.critical(self, "Configuration Error", "SOFiSTiK path is not set. Please configure SOFiSTiK path.")
            return

        try:
            H_value = float(H)
            V_value = float(V)
            epsilon_value = float(epsilon)
        except ValueError:
            print("Error: H, V, and epsilon must be numbers.")
            QMessageBox.critical(self, "Input Error", "H, V, and epsilon must be numbers.")
            return

        # Start the process in a new thread so that the GUI remains responsive
        self.run_button.setEnabled(False)
        self.config_button.setEnabled(False)
        threading.Thread(
            target=self.execute_script,
            args=(V_value, H_value, epsilon_value, dat_file)
        ).start()

    def execute_script(self, V, H, epsilon, dat_file):
        # Perform the calculation process with Iteration from flamb
        try:
            cdb_file_path = dat_file.replace('.dat', '.cdb')
            iteration = Iteration(V, H, epsilon, cdb_file_path, dat_file, self.sofistik_path)
            iteration.initialize()
            iteration.loop()
            print("Process completed successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Re-enable the Run and Configuration buttons
            self.run_button.setEnabled(True)
            self.config_button.setEnabled(True)

    def append_output_text(self, message):
        # Append text to the output_text widget
        if message:
            self.output_text.append(message)

    def open_configuration_dialog(self):
        dialog = ConfigurationDialog(self.sofistik_path, self)
        if dialog.exec():
            # Update configuration and paths
            self.sofistik_path = dialog.sofistik_path
            self.save_sofistik_path(self.sofistik_path)
            print("SOFiSTiK path updated to {}".format(self.sofistik_path))

    def save_sofistik_path(self, sofistik_path):
        config = configparser.ConfigParser()
        config['SOFiSTiK'] = {'sofistik_path': sofistik_path}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def closeEvent(self, event):
        # Restore original stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
