import sqlite3
import os
import hashlib
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DB_DIR = os.path.join(PROJECT_ROOT, "data_files")
DB_PATH = os.path.join(DB_DIR, "conciliacion.db")

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def _get_db_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def verify_user(username: str, password: str) -> bool:
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT contraseña FROM Usuarios WHERE nombre_usuario = ?", (username,))
    user_row = cursor.fetchone()
    conn.close()
    
    if user_row:
        stored_hash = user_row['contraseña']
        input_hash = _hash_password(password)
        return stored_hash == input_hash
        
    return False

def add_user(first_name: str, last_name: str, username: str, email: str, password: str) -> tuple[bool, str]:
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    password_hash = _hash_password(password)
    default_role = "usuario"
    
    try:
        cursor.execute(
            "INSERT INTO Usuarios (nombre, apellido, nombre_usuario, correo, contraseña, rol) VALUES (?, ?, ?, ?, ?, ?)",
            (first_name, last_name, username, email, password_hash, default_role)
        )
        conn.commit()
        return True, "Usuario registrado exitosamente."
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Usuarios.nombre_usuario" in str(e):
            return False, "El nombre de usuario ya existe."
        elif "UNIQUE constraint failed: Usuarios.correo" in str(e):
            return False, "El correo electrónico ya está en uso."
        else:
            return False, f"Error inesperado: {e}"
    finally:
        conn.close()

def update_user(original_username: str, new_first_name: str, new_last_name: str, new_email: str, new_password: str | None = None) -> tuple[bool, str]:
    conn = _get_db_connection()
    cursor = conn.cursor()

    query = "UPDATE Usuarios SET nombre = ?, apellido = ?, correo = ? WHERE nombre_usuario = ?"
    params = [new_first_name, new_last_name, new_email, original_username]

    if new_password:
        query = "UPDATE Usuarios SET nombre = ?, apellido = ?, correo = ?, contraseña = ? WHERE nombre_usuario = ?"
        params = [new_first_name, new_last_name, new_email, _hash_password(new_password), original_username]

    try:
        cursor.execute(query, params)
        conn.commit()
        return True, "Usuario actualizado exitosamente."
    except sqlite3.IntegrityError as e:
        return False, f"Error de integridad: {e}"
    finally:
        conn.close()

def delete_user(username: str) -> tuple[bool, str]:
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Usuarios WHERE nombre_usuario = ?", (username,))
        conn.commit()
        return True, "Usuario eliminado exitosamente."
    except sqlite3.Error as e:
        return False, f"Error al eliminar usuario: {e}"
    finally:
        conn.close()

def get_all_users() -> list:
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT nombre, apellido, correo, nombre_usuario FROM Usuarios ORDER BY nombre")
    users = cursor.fetchall()
    
    conn.close()
    return users