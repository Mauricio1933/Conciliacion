import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QWidget,
    QMessageBox, QDialogButtonBox, QSizePolicy, QComboBox
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../../assets"))
from src.gui.widgets.barra_custom import CustomTitleBar
from src.logic.database import update_user, add_user

class UserFormDialog(QDialog):
    def __init__(self, user_data: dict | None = None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.is_edit_mode = user_data is not None

        self.setMinimumWidth(430)
        self.setMinimumHeight(350)
        self.setModal(True)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog) 
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._setup_ui()
        self.setObjectName("UserFormDialog")

        qss_file_path = os.path.join(ASSETS_PATH, "styles", "user_dialog_estilos.qss")
        try:
            with open(qss_file_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Advertencia: No se encontro el archivo de estilos en la ruta: {qss_file_path}")

    def _setup_ui(self):
        self.container_widget = QWidget()
        self.container_widget.setObjectName("DialogContainerWidget")

        main_layout = QVBoxLayout(self.container_widget)
        main_layout.setSpacing(0) 
        main_layout.setContentsMargins(1, 1, 1, 1)

        self.title_bar = CustomTitleBar(self, show_maximize=False, show_icon=True, show_minimize=False)
        
        main_layout.addWidget(self.title_bar)

        title_text = "Editar Información del Usuario" if self.is_edit_mode else "Agregar Nuevo Usuario"
        title = QLabel(title_text)
        title.setObjectName("DialogTitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

    
        name_layout = QHBoxLayout()
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("Nombre")
        self.first_name_input.setObjectName("FirstNameInput")
        self.first_name_input.setText(self.user_data.get('nombre', '') if self.is_edit_mode else "")
        self.first_name_input.setFixedHeight(40)
        self.first_name_input.addAction(QIcon(os.path.join(ASSETS_PATH, "icons", "user_light.svg")), QLineEdit.ActionPosition.LeadingPosition)
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Apellido")
        self.last_name_input.setObjectName("LastNameInput")
        self.last_name_input.setText(self.user_data.get('apellido', '') if self.is_edit_mode else "")
        self.last_name_input.setFixedHeight(40)
        self.last_name_input.addAction(QIcon(os.path.join(ASSETS_PATH, "icons", "user_light.svg")), QLineEdit.ActionPosition.LeadingPosition)

        name_layout.addWidget(self.first_name_input)
        name_layout.addWidget(self.last_name_input)
        form_layout.addLayout(name_layout)

        if self.is_edit_mode:
            self.username_display = QLabel(f"Usuario: {self.user_data.get('nombre_usuario', '')}")
            self.username_display.setObjectName("UsernameDisplayLabel")
            form_layout.addWidget(self.username_display)
            
                                
            status_layout = QHBoxLayout()
            lbl_status = QLabel("Estado:")
            lbl_status.setObjectName("LabelStatus") 
            self.status_combo = QComboBox()
            self.status_combo.addItems(["Activo", "Inactivo"])
            status_val = self.user_data.get('estado', 'activo')
            if not status_val: status_val = 'activo'
            current_status = status_val.capitalize()
            
            self.status_combo.setCurrentText(current_status if current_status in ["Activo", "Inactivo"] else "Activo")
            self.status_combo.setFixedHeight(35)
            status_layout.addWidget(lbl_status)
            status_layout.addWidget(self.status_combo)
            form_layout.addLayout(status_layout)
        else:
            self.username_input = QLineEdit()
            self.username_input.setPlaceholderText("Nombre de usuario")
            self.username_input.setObjectName("UsernameInput")
            self.username_input.setFixedHeight(40)
            self.username_input.addAction(QIcon(os.path.join(ASSETS_PATH, "icons", "user_light.svg")), QLineEdit.ActionPosition.LeadingPosition)
            form_layout.addWidget(self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setObjectName("EmailInput")
        self.email_input.setText(self.user_data.get('correo', '') if self.is_edit_mode else "")
        self.email_input.setFixedHeight(40)
        self.email_input.addAction(QIcon(os.path.join(ASSETS_PATH, "icons", "email_icon.svg")), QLineEdit.ActionPosition.LeadingPosition)

        password_layout = QHBoxLayout()
        password_placeholder = "Nueva contraseña " if self.is_edit_mode else "Contraseña"
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(password_placeholder)
        self.password_input.setObjectName("PasswordInput")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.addAction(QIcon(os.path.join(ASSETS_PATH, "icons", "lock_red.svg")), QLineEdit.ActionPosition.LeadingPosition)

        confirm_placeholder = "Confirmar contraseña" if self.is_edit_mode else "Confirmar contraseña"
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText(confirm_placeholder)
        self.confirm_password_input.setObjectName("ConfirmPasswordInput")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setFixedHeight(40)
        self.confirm_password_input.addAction(QIcon(os.path.join(ASSETS_PATH, "icons", "lock_red.svg")), QLineEdit.ActionPosition.LeadingPosition)

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.confirm_password_input)


        form_layout.addWidget(self.email_input)
        form_layout.addLayout(password_layout)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 10, 20, 20)
        content_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        save_button = button_box.button(QDialogButtonBox.StandardButton.Save)
        save_button.setText("Guardar")
        save_button.setObjectName("DialogSaveButton")
        
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Cancelar")
        cancel_button.setObjectName("DialogCancelButton")

        content_layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(content_widget)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(self.container_widget)

    def accept(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if self.is_edit_mode:
            if not all([first_name, last_name, email]):
                QMessageBox.warning(self, "Campos Incompletos", "Nombre, apellido y correo no pueden estar vacíos.")
                return

            new_password = None
            if password:
                if password != confirm_password:
                    QMessageBox.warning(self, "Error de Contraseña", "Las nuevas contraseñas no coinciden.")
                    return
                new_password = password

            new_status = self.status_combo.currentText().lower()

            original_username = self.user_data['nombre_usuario']
            success, message = update_user(
                original_username=original_username,
                new_first_name=first_name,
                new_last_name=last_name,
                new_email=email,
                new_password=new_password,
                new_status=new_status
            )

            if success:
                QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente.")
                super().accept()
            else:
                QMessageBox.critical(self, "Error de Actualización", message)
        else:
            username = self.username_input.text()
            if not all([first_name, last_name, username, email, password, confirm_password]):
                QMessageBox.warning(self, "Campos Incompletos", "Por favor, rellene todos los campos.")
                return

            if password != confirm_password:
                QMessageBox.warning(self, "Error de Contraseña", "Las contraseñas no coinciden.")
                return

            success, message = add_user(first_name, last_name, username, email, password)

            if success:
                QMessageBox.information(self, "Registro Exitoso", message)
                super().accept()
            else:
                QMessageBox.critical(self, "Error de Registro", message)