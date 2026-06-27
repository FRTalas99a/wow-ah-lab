# Para obtecnión de tokens: tipear en terminal

    python -c "
    import sys, os
    sys.path.append('ahlabenv')
    from config.secrets import CLIENT_ID, CLIENT_SECRET, REGION
    import requests
    r = requests.post(f'https://{REGION}.battle.net/oauth/token', auth=(CLIENT_ID, CLIENT_SECRET), data={'grant_type': 'client_credentials'})
    print(r.json()['access_token'])
    "

# Para obtención de 20 ítems más activos del AH: tipear en terminal

    python -c "
    import sys, os, requests
    sys.path.append('ahlabenv')
    from config.secrets import CLIENT_ID, CLIENT_SECRET
    from config.config import REGION, REALM_ID

    r = requests.post(f'https://{REGION}.battle.net/oauth/token', auth=(CLIENT_ID, CLIENT_SECRET), data={'grant_type': 'client_credentials'})
    token = r.json()['access_token']

    r2 = requests.get(f'https://{REGION}.api.blizzard.com/data/wow/connected-realm/{REALM_ID}/auctions', headers={'Authorization': f'Bearer {token}'}, params={'namespace': f'dynamic-{REGION}', 'locale': 'en_US'})
    auctions = r2.json().get('auctions', [])

  ## Contamos cuántos listings tiene cada item

    from collections import Counter
    item_counts = Counter(a['item']['id'] for a in auctions)

  ## Mostramos los 20 items con más listings

    print('Items con más listings en tu AH ahora mismo:')
    for item_id, count in item_counts.most_common(20):
    print(f' item_id: {item_id} → {count} listings')
    "
