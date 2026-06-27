# tests/test.py
import sys
import os
import json
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.secrets import CLIENT_ID, CLIENT_SECRET, REGION

# === PASO 1: Obtener el Access Token ===
def get_access_token():
    url = f"https://{REGION}.battle.net/oauth/token"
    response = requests.post(
        url,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Error al obtener token: {response.status_code}")
        print(response.text)
        return None

# === PASO 2: Conseguir los datos del AH ===
def get_auction_house_data(realm_id, token):
    url = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{realm_id}/auctions"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"namespace": f"dynamic-{REGION}", "locale": "en_US"}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener datos del AH: {response.status_code}")
        return None

# === MAIN ===
if __name__ == "__main__":
    print("Obteniendo token de acceso...")
    token = get_access_token()

    if token:
        print(f"✅ Token obtenido: {token[:20]}...")

        realm_id = 1136  # Stormrage-US, solo para probar
        print(f"\nDescargando datos del AH (realm {realm_id})...")
        ah_data = get_auction_house_data(realm_id, token)

        if ah_data:
            auctions = ah_data.get("auctions", [])
            print(f"\n✅ Éxito! Encontré {len(auctions)} listings en el AH.")
            print("\nPrimeros 3 listings:")
            for auction in auctions[:3]:
                print(json.dumps(auction, indent=2))