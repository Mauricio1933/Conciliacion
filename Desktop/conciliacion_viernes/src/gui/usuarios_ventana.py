from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy,
    QPushButton, QHBoxLayout, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QCursor
import os
from functools import partial

from src.gui.dialogs.user_form_dialog import UserFormDialog
from src.logic.database import get_all_users

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.abspath(os.path.join(BASE_PATH, "../../assets"))

class UsersView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentArea")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.main_view_layout = QVBoxLayout(self)
        self.main_view_layout.setContentsMargins(30, 20, 30, 30)
        self.main_view_layout.setSpacing(15)
        
        self._setup_ui()

    def _setup_ui(self):
        top_actions_layout = QHBoxLayout()
        top_actions_layout.setContentsMargins(0, 0, 0, 0)
        top_actions_layout.addStretch(1)
        
        action_v_container = QWidget()
        action_v_layout = QVBoxLayout(action_v_container)
        action_v_layout.setContentsMargins(0, 0, 0, 0)
        action_v_layout.setSpacing(5)
        action_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        add_user_text_label = QLabel("Agregar Usuario")
        add_user_text_label.setObjectName("AddUserTextLabel")
        add_user_text_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        action_v_layout.addWidget(add_user_text_label)

        self.btn_add_user_icon = QPushButton()
        self.btn_add_user_icon.setObjectName("BtnAddUserIcon")
        self.btn_add_user_icon.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_user_icon.setFixedSize(50, 50)
        
        add_user_icon_filename = "add_user_icon.svg"
        add_user_icon_path = os.path.join(ASSETS_PATH, "icons", add_user_icon_filename)
        
        if os.path.exists(add_user_icon_path):
            self.btn_add_user_icon.setIcon(QIcon(add_user_icon_path))
            self.btn_add_user_icon.setIconSize(QSize(45, 45))
        else:
            self.btn_add_user_icon.setIcon(QIcon.fromTheme("list-add"))
            
        self.btn_add_user_icon.clicked.connect(self.add_user_clicked)
        action_v_layout.addWidget(self.btn_add_user_icon, alignment=Qt.AlignmentFlag.AlignRight)
        
        top_actions_layout.addWidget(action_v_container)
        self.main_view_layout.addLayout(top_actions_layout)
        title_label = QLabel("Usuarios")
        title_label.setObjectName("RecordsTitle")
        self.main_view_layout.addWidget(title_label)
        
        self.user_cards_container = QWidget()
        self.user_cards_layout = QVBoxLayout(self.user_cards_container)
        self.user_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.user_cards_layout.setSpacing(15)
        
        self.refresh_user_list()
        
        self.main_view_layout.addWidget(self.user_cards_container)
        self.main_view_layout.addStretch(1)

    def refresh_user_list(self):
        while self.user_cards_layout.count():
            child = self.user_cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    sub_child = child.layout().takeAt(0)
                    if sub_child.widget():
                        sub_child.widget().deleteLater()

        all_users = get_all_users()
        if not all_users:
            no_users_label = QLabel("No hay usuarios registrados en la base de datos.")
            no_users_label.setObjectName("NoUsersLabel")
            no_users_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.user_cards_layout.addWidget(no_users_label)
        else:
            for user in all_users:
                full_name = f"{user['nombre']} {user['apellido']}"
                user_card = self._create_user_card(dict(user))
                center_hbox = QHBoxLayout()
                center_hbox.setContentsMargins(0, 0, 0, 0)
                center_hbox.addWidget(user_card)
                self.user_cards_layout.addLayout(center_hbox)

    def add_user_clicked(self):
        dialog = UserFormDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_user_list()

    def _create_user_card(self, user_data: dict) -> QWidget:
        full_name = f"{user_data['nombre']} {user_data['apellido']}"
        user_email = user_data['correo']
        user_name_id = user_data['nombre_usuario']

        user_card = QWidget()
        user_card.setObjectName("ThinRectangle")
        user_card.setFixedHeight(60)
        user_card.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Fixed
        )
        
        card_layout = QHBoxLayout(user_card)
        card_layout.setContentsMargins(10, 5, 10, 5)
        card_layout.setSpacing(15)
        
        icon_label = QLabel()
        icon_label.setObjectName("UserIconLabel")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_filename = "user_light.svg"
        icon_path = os.path.join(ASSETS_PATH, "icons", icon_filename)
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(QSize(35, 35), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("👤")
            icon_label.setFont(QFont("Inter", 16))
        
        card_layout.addWidget(icon_label)
        
        user_info_widget = QWidget()
        user_info_layout = QHBoxLayout(user_info_widget) 
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(15)
        
        name_label = QLabel(full_name)
        name_label.setObjectName("UserNameLabel")
        
        name_container = QWidget()
        name_container.setLayout(QHBoxLayout())
        name_container.layout().setContentsMargins(0, 0, 0, 0)
        name_container.layout().addWidget(name_label)
        name_container.layout().setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        user_info_layout.addWidget(name_container)
        email_group_widget = QWidget()
        email_group_layout = QHBoxLayout(email_group_widget)
        email_group_layout.setContentsMargins(0, 0, 0, 0)
        email_group_layout.setSpacing(5)
        email_group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        email_icon_label = QLabel()
        email_icon_label.setObjectName("EmailIconLabel")
        email_icon_filename = "email_icon.svg"
        email_icon_path = os.path.join(ASSETS_PATH, "icons", email_icon_filename)
        if os.path.exists(email_icon_path):
            pixmap_email = QPixmap(email_icon_path)
            email_icon_label.setPixmap(pixmap_email.scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            email_icon_label.setText("📧")
        
        email_group_layout.addWidget(email_icon_label)
        
        email_label = QLabel(user_email)
        email_label.setObjectName("UserEmailLabel")
        email_group_layout.addWidget(email_label)
        user_info_layout.addWidget(email_group_widget)

        username_group_widget = QWidget()
        username_group_layout = QHBoxLayout(username_group_widget)
        username_group_layout.setContentsMargins(0, 0, 0, 0)
        username_group_layout.setSpacing(5)
        username_group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        username_icon_label = QLabel()
        username_icon_label.setObjectName("UsernameIconLabel")
        username_icon_filename = "id_icon.svg"
        username_icon_path = os.path.join(ASSETS_PATH, "icons", username_icon_filename)
        
        if os.path.exists(username_icon_path):
            pixmap_username = QPixmap(username_icon_path)
            username_icon_label.setPixmap(pixmap_username.scaled(QSize(40, 40), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            username_icon_label.setText("@")
            
        username_group_layout.addWidget(username_icon_label)
        
        username_label = QLabel(user_name_id)
        username_label.setObjectName("UsernameIDLabel")
        username_group_layout.addWidget(username_label)
        user_info_layout.addWidget(username_group_widget)
        
                            
        user_role = user_data.get('rol', 'asistente').capitalize()
        status_val = user_data.get('estado', 'activo')
        if not status_val: status_val = 'activo'
        user_status = status_val.capitalize()
        
        status_color = "#4CAF50" if user_status == "Activo" else "#F44336"
        
        status_label = QLabel(f"{user_role} | {user_status}")
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold; margin-left: 15px;")
        status_label.setObjectName("UserStatusLabel")
        status_label.setFont(QFont("Inter", 10))
        user_info_layout.addWidget(status_label)
                            
        
        user_info_layout.addStretch(1)
        
        card_layout.addWidget(user_info_widget)
        
        edit_button = QPushButton()
        edit_button.setObjectName("EditButton")
        edit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_button.setFixedSize(40, 40)
        
        edit_icon_filename = "editar_icon.svg"
        edit_icon_path = os.path.join(ASSETS_PATH, "icons", edit_icon_filename)
        if os.path.exists(edit_icon_path):
            edit_button.setIcon(QIcon(edit_icon_path))
            edit_button.setIconSize(QSize(30, 30))
        else:
            edit_button.setText("✏️")
        
        edit_button.clicked.connect(partial(self.open_edit_dialog, user_data))
        card_layout.addWidget(edit_button)
        

        
        return user_card

    def open_edit_dialog(self, user_data: dict):
        dialog = UserFormDialog(user_data, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_user_list()
            

