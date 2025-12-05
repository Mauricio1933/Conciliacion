import os
import sqlite3
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

def initialize_db():
    conn = _get_db_connection()
    cursor = conn.cursor()
    
                                                                           
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            nombre_usuario TEXT UNIQUE NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL,
            rol TEXT DEFAULT 'asistente',
            estado TEXT DEFAULT 'activo'
        )
    """)
    
                                                          
    try:
        cursor.execute("ALTER TABLE Usuarios ADD COLUMN rol TEXT DEFAULT 'asistente'")
    except sqlite3.OperationalError: pass 
    
    try:
        cursor.execute("ALTER TABLE Usuarios ADD COLUMN estado TEXT DEFAULT 'activo'")
    except sqlite3.OperationalError: pass 
    
                                          
    cursor.execute("SELECT COUNT(*) as count FROM Usuarios WHERE nombre_usuario = 'admin'")
    count_result = cursor.fetchone()
    if count_result and count_result['count'] == 0:
        admin_pass = _hash_password('admin')
        try:
            cursor.execute(
                "INSERT INTO Usuarios (nombre, apellido, nombre_usuario, correo, contraseña, rol, estado) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ('Administrador', 'Sistema', 'admin', 'admin@sistema.com', admin_pass, 'admin', 'activo')
            )
            print("INFO: Usuario 'admin' creado por defecto.")
        except sqlite3.IntegrityError as e:
            print(f"ADVERTENCIA: No se pudo crear admin por defecto: {e}") 

    conn.commit()
    conn.close()

                                                                    
initialize_db()

def verify_user(username: str, password: str) -> dict | None:
    """Verifica credenciales y estado. Retorna dict con datos de usuario si éxito, None si falla."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Usuarios WHERE nombre_usuario = ?", (username,))
    user_row = cursor.fetchone()
    conn.close()
    
    if user_row:
        stored_hash = user_row['contraseña']
        input_hash = _hash_password(password)
        
        if stored_hash == input_hash:
                              
            if user_row['estado'] != 'activo':
                return {"error": "Usuario inactivo. Contacte al administrador."}
            
                                                  
            return {
                "nombre": user_row['nombre'],
                "apellido": user_row['apellido'],
                "usuario": user_row['nombre_usuario'],
                "rol": user_row['rol'],
                "estado": user_row['estado']
            }
        
    return None

def add_user(first_name: str, last_name: str, username: str, email: str, password: str, role: str = "asistente") -> tuple[bool, str]:
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    password_hash = _hash_password(password)
                                                                      
    
                                                               
    cursor.execute("SELECT COUNT(*) as count FROM Usuarios")
    if cursor.fetchone()['count'] == 0:
        role = "admin"

    try:
        cursor.execute(
            "INSERT INTO Usuarios (nombre, apellido, nombre_usuario, correo, contraseña, rol, estado) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (first_name, last_name, username, email, password_hash, role, "activo")
        )
        conn.commit()
        return True, "Usuario registrado exitosamente."
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Usuarios.nombre_usuario" in str(e):
            return False, "El nombre de usuario ya existe."
        elif "UNIQUE constraint failed: Usuarios.correo" in str(e):
            return False, "El correo electronico ya esta en uso."
        else:
            return False, f"Error inesperado: {e}"
    finally:
        conn.close()

def update_user(original_username: str, new_first_name: str, new_last_name: str, new_email: str, new_password: str | None = None, new_status: str = None) -> tuple[bool, str]:
    conn = _get_db_connection()
    cursor = conn.cursor()

                                                   
    fields = ["nombre = ?", "apellido = ?", "correo = ?"]
    params = [new_first_name, new_last_name, new_email]

    if new_password:
        fields.append("contraseña = ?")
        params.append(_hash_password(new_password))
    
    if new_status:
        fields.append("estado = ?")
        params.append(new_status)

    query = f"UPDATE Usuarios SET {', '.join(fields)} WHERE nombre_usuario = ?"
    params.append(original_username)

    try:
        cursor.execute(query, params)
        conn.commit()
        return True, "Usuario actualizado exitosamente."
    except sqlite3.IntegrityError as e:
        return False, f"Error de integridad: {e}"
    finally:
        conn.close()

def get_all_users() -> list:
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT nombre, apellido, correo, nombre_usuario, rol, estado FROM Usuarios ORDER BY nombre")
    users = cursor.fetchall()                              
    
    conn.close()
                                                                     
    return [dict(row) for row in users]

def get_user_by_username(username: str):
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE nombre_usuario = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row: return dict(row)
    return None