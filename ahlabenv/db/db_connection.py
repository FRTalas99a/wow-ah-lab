# db/db_connection.py
import mysql.connector
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.secrets import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    """
    Crea y devuelve una conexión a MySQL.
    Usamos esta función en todos los scripts que necesiten la DB.
    """
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return connection

# Test de conexión
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Conexión a MySQL exitosa!")
        conn.close()
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        
def test_insert():
    """
    Inserta datos de prueba para verificar que los INSERTs funcionan.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Insertamos tu realm
    cursor.execute("""
        INSERT IGNORE INTO realms (realm_id, name, region, timezone)
        VALUES (1136, 'Stormrage', 'us', 'America/New_York')
    """)

    # Insertamos un item de prueba
    cursor.execute("""
        INSERT IGNORE INTO items (item_id, name, category, subcategory)
        VALUES (191501, 'Flask of Tempered Aggression', 'consumable', 'flask')
    """)

    conn.commit()
    print(f"✅ INSERT exitoso! Filas insertadas: {cursor.rowcount}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Conexión a MySQL exitosa!")
        conn.close()
        test_insert()
    except Exception as e:
        print(f"❌ Error: {e}")