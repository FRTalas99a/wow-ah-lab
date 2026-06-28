# collectors/ah_collector.py
import sys
import os
import requests
from datetime import datetime
import mysql.connector

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.secrets import CLIENT_ID, CLIENT_SECRET, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from config.config import REGION, REALM_ID, MONITORED_ITEMS

def get_access_token():
    """Obtiene token de acceso de Blizzard."""
    url = f"https://{REGION}.battle.net/oauth/token"
    response = requests.post(
        url,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )
    response.raise_for_status()
    return response.json()["access_token"]

def get_ah_data(token):
    """Descarga todos los auctions del AH de tu realm."""
    url = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{REALM_ID}/auctions"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params={"namespace": f"dynamic-{REGION}", "locale": "en_US"}
    )
    response.raise_for_status()
    return response.json().get("auctions", [])

def calculate_metrics(listings):
    """Calcula métricas agregadas para un item."""
    if not listings:
        return None

    prices = sorted(listings, key=lambda x: x['price_per_unit'])

    min_price = prices[0]['price_per_unit']
    max_price = prices[-1]['price_per_unit']

    total_value = sum(l['price_per_unit'] * l['quantity'] for l in listings)
    total_qty = sum(l['quantity'] for l in listings)
    avg_price = total_value / total_qty if total_qty > 0 else 0

    mid = len(prices) // 2
    median_price = prices[mid]['price_per_unit']

    return {
        'min_price': round(min_price, 2),
        'max_price': round(max_price, 2),
        'avg_price': round(avg_price, 2),
        'median_price': round(median_price, 2),
        'total_quantity': total_qty,
        'listing_count': len(listings)
    }

def save_snapshots(cursor, snapshots):
    """Inserta los snapshots en la base de datos."""
    insert_query = """
        INSERT INTO ah_snapshots
        (item_id, realm_id, captured_at, min_price, max_price,
         avg_price, median_price, total_quantity, listing_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    captured_at = datetime.now()
    rows_inserted = 0

    for item_id, metrics in snapshots.items():
        values = (
            item_id, REALM_ID, captured_at,
            metrics['min_price'], metrics['max_price'],
            metrics['avg_price'], metrics['median_price'],
            metrics['total_quantity'], metrics['listing_count']
        )
        cursor.execute(insert_query, values)
        rows_inserted += 1

    return rows_inserted

def run_collection():
    """Función principal. Une todo el proceso."""
    print(f"[{datetime.now()}] Iniciando colección de datos...")

    # 1. Conexión a MySQL
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME,
            port=12289,
            ssl_disabled=False
            )
        cursor = conn.cursor(dictionary=True)
        print("✅ Conectado a MySQL")
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return
    # 2. Token de Blizzard
    try:
        token = get_access_token()
        print("✅ Token de Blizzard obtenido")
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        conn.close()
        return

    # 3. Descargar datos del AH
    try:
        all_auctions = get_ah_data(token)
        print(f"✅ Descargados {len(all_auctions)} listings del AH")
    except Exception as e:
        print(f"❌ Error descargando AH: {e}")
        conn.close()
        return

    # 4. Filtrar y agrupar por item monitoreado
    items_data = {}
    for auction in all_auctions:
        item_id = auction.get("item", {}).get("id")

        if item_id not in MONITORED_ITEMS:
            continue

        buyout = auction.get("buyout", 0)
        quantity = auction.get("quantity", 1)

        if buyout == 0:
            continue

        price_per_unit = (buyout / quantity) / 10000  # cobre → gold

        if item_id not in items_data:
            items_data[item_id] = []

        items_data[item_id].append({
            'price_per_unit': price_per_unit,
            'quantity': quantity
        })

    print(f"📊 Items monitoreados con listings activos: {len(items_data)}")

    # 5. Calcular métricas y guardar
    snapshots = {}
    for item_id, listings in items_data.items():
        metrics = calculate_metrics(listings)
        if metrics:
            snapshots[item_id] = metrics
            name = MONITORED_ITEMS[item_id]
            print(f"   → {name}: min={metrics['min_price']}g | "
                  f"avg={metrics['avg_price']}g | "
                  f"qty={metrics['total_quantity']}")

    # 6. Insertar en MySQL
    if snapshots:
        rows = save_snapshots(cursor, snapshots)
        conn.commit()
        print(f"\n✅ Guardados {rows} snapshots en MySQL")
    else:
        print("\n⚠️ Ningún item monitoreado encontrado en el AH")

    cursor.close()
    conn.close()
    print(f"[{datetime.now()}] Colección completada.\n")

if __name__ == "__main__":
    run_collection()