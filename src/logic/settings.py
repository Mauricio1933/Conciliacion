from PyQt6.QtCore import QSettings

ORGANIZATION_NAME = "Conciliar"
APPLICATION_NAME = "app de conciliacion"

def save_credentials(username: str, password: str):
    settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
    settings.setValue("username", username)
    settings.setValue("password", password)

def load_credentials() -> tuple[str | None, str | None]:
    settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
    username = settings.value("username")
    password = settings.value("password")
    return username, password

def clear_credentials():
    settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
    settings.remove("username")
    settings.remove("password")