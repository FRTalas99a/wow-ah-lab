# tests/find_realm.py
import sys, os, requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.secrets import CLIENT_ID, CLIENT_SECRET, REGION

# Obtenemos token
r = requests.post(
    f"https://{REGION}.battle.net/oauth/token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={"grant_type": "client_credentials"}
)
token = r.json()["access_token"]

# Buscamos todos los realms
response = requests.get(
    f"https://{REGION}.api.blizzard.com/data/wow/realm/index",
    headers={"Authorization": f"Bearer {token}"},
    params={"namespace": f"dynamic-{REGION}", "locale": "es_MX"}
)

# Filtramos solo Quel'Thalas
realms = response.json().get("realms", [])
for realm in realms:
    if "quel" in realm["name"].lower() or "thalas" in realm["name"].lower():
        print(realm)