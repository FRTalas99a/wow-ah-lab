# 🏰 WoW Auction House — Laboratorio Cuantitativo
### Guía Completa: Arquitectura · Roadmap · Economía · Código

---

## 📌 ÍNDICE

1. [¿Qué estás construyendo realmente?](#1-qué-estás-construyendo-realmente)
2. [Economía de WoW: fundamentos que necesitás entender](#2-economía-de-wow-fundamentos)
3. [Arquitectura técnica inicial](#3-arquitectura-técnica-inicial)
4. [Guía pedagógica: APIs, Python, SQL explicados desde cero](#4-guía-pedagógica)
5. [Blizzard API: cómo conectarte paso a paso](#5-blizzard-api-paso-a-paso)
6. [Estructura de carpetas del proyecto](#6-estructura-de-carpetas)
7. [Base de datos: diseño de tablas SQL](#7-diseño-de-base-de-datos)
8. [Insertar datos en MySQL desde Python](#8-insertar-datos-en-mysql-desde-python)
9. [Automatización en PythonAnywhere (cron jobs)](#9-pythonanywhere-paso-a-paso)
10. [Fases evolutivas del proyecto](#10-fases-evolutivas)
11. [Calendario semanal: receta práctica](#11-calendario-semanal)
12. [Qué medir primero y por qué](#12-qué-medir-primero-y-por-qué)
13. [Riesgos que probablemente estás ignorando](#13-riesgos-conceptuales)
14. [Estrategia desde la perspectiva del Goblin experto](#14-estrategia-goblin)

---

## 1. ¿Qué estás construyendo realmente?

Antes del código, necesitás tener claro el modelo mental. Estás construyendo esto:

```
API de Blizzard
     │
     ▼
Script Python (recolector)
     │
     ▼
Base de datos MySQL (memoria del sistema)
     │
     ▼
Scripts de análisis (cerebro)
     │
     ▼
Insights accionables (decisiones de mercado)
```

Cada capa tiene un rol:

- **API de Blizzard**: es la "fuente de verdad". Te dice qué se está vendiendo, a qué precio y en qué cantidad ahora mismo.
- **Script Python**: actúa como tu agente de campo. Sale a buscar datos, los ordena y los guarda.
- **MySQL**: es tu archivo histórico. Sin él, solo ves el presente; con él, podés ver tendencias.
- **Scripts de análisis**: calculan métricas (precio promedio, volatilidad, spread, volumen).
- **Insights**: la razón de todo esto. ¿Conviene comprar Ores ahora? ¿Hay una oportunidad de flip en Flasks?

---

## 2. Economía de WoW: Fundamentos

### 🧠 El mercado del AH no es eficiente — y eso es tu ventaja

A diferencia de los mercados financieros reales, el AH de WoW está lleno de ineficiencias explotables porque:

- **Los jugadores no tienen memoria histórica.** No saben si el precio de hoy es caro o barato.
- **La mayoría actúa emocionalmente.** Postean al precio más bajo porque "quieren vender rápido".
- **Hay poca coordinación.** Los vendedores compiten entre sí sin estrategia.
- **Los ciclos son predecibles.** Contenido nuevo = demanda predecible en categorías específicas.

### 📅 Los 5 ciclos económicos que gobiernan el AH

**Ciclo 1: El ciclo semanal (Reset Day)**

El día de reset (martes en NA, miércoles en EU) es el evento económico más importante de la semana.

- Guilds de progresión compran consumibles masivamente: Flasks, Potions, Food buffs, Enchants de reparación.
- Los precios de consumibles suben entre un 15% y 40% durante el martes/miércoles.
- Los materiales base (Herbs para Flasks, Ores para Enchants) se agotan o suben poco antes.
- **Estrategia básica**: comprar consumibles el jueves/viernes cuando están baratos. Vender el lunes/martes.

**Ciclo 2: Ciclo de parche (el más poderoso)**

Cuando Blizzard anuncia un nuevo tier de raid o parche importante:

- *Antes del parche*: los jugadores stockean materiales que creen que necesitarán. Precios de mats suben anticipadamente.
- *Día del parche*: caos total. Los precios pueden subir o colapsar según el contenido.
- *Post-parche semana 1*: demanda explosiva de consumibles, BoE de nuevo gear, enchants del nuevo tier.
- *Post-parche semana 3-4*: los farmers llegaron al mercado; los mats bajan, los consumibles se estabilizan.

**Ciclo 3: Ciclo de temporada (inicio/fin de season PvP)**

- Inicio de season PvP: demanda alta de consumibles PvP (pociones específicas, enchants PvP).
- Fin de season: el mercado se contrae, muchos jugadores dejan de jugar.

**Ciclo 4: Ciclo de farming de contenido**

- Semana 1 de nuevo raid: los "sweaties" farmean el raid en heroic/mythic. Hay demanda masiva de consumibles y caída de precios de gear.
- Semana 4-6: el casual llega al tier. Segunda ola de demanda de consumibles pero más moderada.

**Ciclo 5: El ciclo de bots y farmers**

- Hay bots que farmean herbs/ores 24/7. Cuando Blizzard banea oleadas, los precios de mats suben dramáticamente por 48-72 horas.
- Después del baneo, el precio vuelve a su "nivel bot". Esto genera oportunidades de short-selling si tenés stock.

### 🏪 Taxonomía del mercado (lo que vas a analizar)

**Tier 1 - Consumibles de alta rotación** (volumen diario alto, margen por unidad bajo-medio):
- Flasks, Potions, Food buffs, Runes
- Alta liquidez, fácil de entrar y salir
- Muy sensibles al ciclo semanal

**Tier 2 - Materiales base** (volumen altísimo, margen bajo):
- Herbs, Ores, Leather, Cloth
- El mercado más competitivo
- Alta correlación con actividad de bots
- Margen de profit proviene del volumen, no del precio unitario

**Tier 3 - Crafting de gear BoE** (volumen bajo, margen alto):
- Los BoE de nuevo raid tier valen miles de gold la primera semana
- Son el "mercado de lujo" del AH
- Requieren entender el meta de clases/specs para saber qué specs pagan premium

**Tier 4 - Servicios y niche** (muy bajo volumen, margen altísimo):
- Transmog raros, mounts crafteables, legendarios
- Casi imposible de modelar estadísticamente
- Más arte que ciencia

### 👥 Los jugadores como agentes económicos

Para modelar el mercado necesitás entender quiénes son tus contrapartes:

- **El casual (80% del mercado)**: no sabe el precio histórico, vende barato para vender rápido, compra cuando necesita sin comparar.
- **El semi-pro**: usa addons como TradeSkillMaster (TSM), tiene precio mínimo configurado, es tu competidor directo.
- **El Goblin full-time**: tiene cientos de miles de gold, manipula mercados deliberadamente, puede postear debajo del costo para sacar competidores y luego subir precios.
- **El bot**: posta 24/7, detecta tu precio mínimo y lo postea 1 copper abajo. Es ruido en tus datos.

---

## 3. Arquitectura Técnica Inicial

### Principio guía: "Simple ahora, extensible después"

No construyas lo que vas a necesitar en el futuro. Construí lo mínimo que funcione hoy.

### Arquitectura Fase 1 (lo que vas a construir primero)

```
┌─────────────────────────────────────────────────────┐
│                  PythonAnywhere                      │
│                                                     │
│  ┌─────────────┐      ┌──────────────────────────┐  │
│  │  Cron Job   │─────▶│  collector.py            │  │
│  │  cada 4h    │      │  (llama API de Blizzard) │  │
│  └─────────────┘      └──────────┬───────────────┘  │
│                                  │                  │
│                                  ▼                  │
│                       ┌──────────────────────────┐  │
│                       │  MySQL Database          │  │
│                       │  - ah_snapshots          │  │
│                       │  - items                 │  │
│                       │  - price_history         │  │
│                       └──────────────────────────┘  │
│                                  │                  │
│                                  ▼                  │
│                       ┌──────────────────────────┐  │
│                       │  analyzer.py             │  │
│                       │  (calcula métricas)      │  │
│                       └──────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Componentes y sus responsabilidades

**`collector.py`** — El recolector:
- Se autentica con la API de Blizzard.
- Descarga el estado actual del AH (todos los listings activos).
- Limpia y transforma los datos.
- Los inserta en MySQL.

**`analyzer.py`** — El analista:
- Lee los datos históricos de MySQL.
- Calcula precio promedio, volatilidad, volumen.
- Detecta oportunidades de flip.
- Genera un reporte simple (puede ser un archivo de texto o CSV al principio).

**MySQL** — La memoria:
- Guarda snapshots del AH a lo largo del tiempo.
- Te permite preguntar "¿cuál fue el precio promedio de Flask X los últimos 30 días?".

---

## 4. Guía Pedagógica

### ¿Qué es una API? (explicado sin jerga)

Imaginá que el Auction House de WoW es un edificio enorme con datos adentro. Vos querés esos datos pero no tenés acceso directo al edificio. Sin embargo, hay una ventanilla en la pared del edificio con un empleado de Blizzard. Vos te acercás a la ventanilla y decís: "Hola, quiero la lista de todos los items que se están vendiendo ahora en el AH del servidor Stormrage". El empleado busca la información y te la devuelve en un formato estándar (JSON).

Eso es una API. Es una interfaz formal que permite a programas externos pedir y recibir datos de un sistema.

### ¿Qué es JSON?

Es el formato en que la API te devuelve los datos. Se parece a esto:

```json
{
  "auctions": [
    {
      "id": 123456,
      "item": {"id": 191501},
      "buyout": 50000,
      "quantity": 20,
      "time_left": "VERY_LONG"
    },
    {
      "id": 123457,
      "item": {"id": 191501},
      "buyout": 48000,
      "quantity": 5,
      "time_left": "LONG"
    }
  ]
}
```

Python puede leer esto y transformarlo en una tabla que guardás en SQL.

### ¿Qué es MySQL y por qué lo necesitás?

Python puede guardar datos en variables mientras corre, pero cuando el script termina, esos datos desaparecen. MySQL es un sistema de base de datos que guarda los datos de forma permanente en disco. Podés pensar en MySQL como una serie de hojas de cálculo muy poderosas que viven en un servidor y que podés consultar con un lenguaje especial llamado SQL.

### ¿Qué es un cron job?

Es una tarea programada que corre automáticamente en un horario. En lugar de abrir tu compu y correr `python collector.py` cada 4 horas, configurás un cron job que lo hace por vos, incluso mientras dormís. PythonAnywhere te provee una interfaz para configurarlos fácilmente.

---

## 5. Blizzard API: Paso a Paso

### Paso 1: Crear tu cuenta de desarrollador

1. Andá a https://develop.battle.net
2. Creá una cuenta si no tenés una (es gratis).
3. Clickeá en "Create Client".
4. Poné un nombre cualquiera (ej: "WoW AH Lab").
5. En el campo "Redirect URLs" ponés: `http://localhost` (para uso personal).
6. Guardás y Blizzard te da un **Client ID** y un **Client Secret**. Estos son tus credenciales. Guardalos bien, no los compartas.

### Paso 2: Entender la autenticación OAuth 2.0

La API de Blizzard usa un sistema llamado OAuth 2.0 para autenticarse. El flujo es así:

1. Tu script le dice a Blizzard: "Hola, soy el cliente con ID X y secreto Y".
2. Blizzard verifica que esos datos son válidos.
3. Blizzard te manda un **access token** (un string largo y raro).
4. Con ese token, podés hacer llamadas a la API durante ~24 horas.
5. Cuando el token expira, repetís el paso 1.

Esto parece complicado pero son solo 5 líneas de Python.

### Paso 3: Tu primer script real de API

Creá un archivo `test_api.py`:

```python
import requests  # librería para hacer llamadas HTTP (como un navegador pero en código)
import json

# === TUS CREDENCIALES ===
# NUNCA pongas estas credenciales directamente en el código que subís a GitHub
# Usamos variables (por ahora está bien para aprender)
CLIENT_ID = "TU_CLIENT_ID_AQUI"
CLIENT_SECRET = "TU_CLIENT_SECRET_AQUI"
REGION = "us"  # o "eu" según tu servidor

# === PASO 1: Obtener el Access Token ===
def get_access_token():
    """
    Le pedimos un token de acceso a Blizzard.
    Es como mostrar tu credencial en la puerta.
    """
    url = f"https://{REGION}.battle.net/oauth/token"
    
    # Enviamos nuestras credenciales usando autenticación básica
    response = requests.post(
        url,
        auth=(CLIENT_ID, CLIENT_SECRET),  # usuario y contraseña
        data={"grant_type": "client_credentials"}  # tipo de autenticación
    )
    
    # Verificamos que la respuesta fue exitosa (código 200 = OK)
    if response.status_code == 200:
        token_data = response.json()  # convertimos la respuesta JSON a diccionario Python
        return token_data["access_token"]
    else:
        print(f"Error al obtener token: {response.status_code}")
        print(response.text)
        return None

# === PASO 2: Conseguir los datos del AH ===
def get_auction_house_data(realm_id, token):
    """
    Descarga todos los listings actuales del AH de un realm.
    realm_id: el ID numérico del servidor (ej: 1136 = Stormrage US)
    """
    url = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{realm_id}/auctions"
    
    headers = {
        "Authorization": f"Bearer {token}"  # incluimos el token en cada llamada
    }
    
    params = {
        "namespace": f"dynamic-{REGION}",
        "locale": "en_US"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al obtener datos del AH: {response.status_code}")
        return None

# === MAIN: Ponemos todo junto ===
if __name__ == "__main__":
    print("Obteniendo token de acceso...")
    token = get_access_token()
    
    if token:
        print(f"Token obtenido: {token[:20]}...")  # mostramos solo los primeros caracteres
        
        # realm_id 1136 es Stormrage-US. Buscá el tuyo en:
        # https://us.api.blizzard.com/data/wow/realm/index?namespace=dynamic-us&locale=en_US&access_token=TU_TOKEN
        realm_id = 1136
        
        print(f"\nDescargando datos del AH (realm {realm_id})...")
        ah_data = get_auction_house_data(realm_id, token)
        
        if ah_data:
            auctions = ah_data.get("auctions", [])
            print(f"\n✅ Éxito! Encontré {len(auctions)} listings en el AH.")
            
            # Mostramos los primeros 3 para ver cómo se ven
            print("\nPrimeros 3 listings:")
            for auction in auctions[:3]:
                print(json.dumps(auction, indent=2))
```

Para correr esto: `python test_api.py`

### Paso 4: Encontrar el ID de tu realm

Todos los servidores tienen un ID. Para encontrar el tuyo:

1. Primero obtené un token corriendo el script anterior.
2. Abrí tu navegador y andá a:
   `https://us.api.blizzard.com/data/wow/realm/index?namespace=dynamic-us&locale=en_US&access_token=TU_TOKEN`
3. Buscá el nombre de tu servidor en la lista y anotá su ID.

Para servidores europeos, reemplazá `us` por `eu` en la URL y el namespace.

### Paso 5: Entender los datos que recibís

Cada auction tiene esta estructura:

```python
{
    "id": 123456,           # ID único del listing
    "item": {
        "id": 191501,       # ID del item (el mismo en todos los servidores)
        "modifiers": [...]  # variantes del item (ilvl, etc.)
    },
    "buyout": 50000,        # precio total en cobre (50000 = 5 gold)
    "quantity": 20,         # cantidad en el stack
    "time_left": "LONG"     # tiempo restante: SHORT/MEDIUM/LONG/VERY_LONG
}
```

**Importante sobre los precios**: La API devuelve precios en **cobre**. Para convertir:
- 1 gold = 10,000 cobre
- Si `buyout = 500000`, eso es 50 gold.
- Precio por unidad = `buyout / quantity`

---

## 6. Estructura de Carpetas

Organizá tu proyecto así desde el principio. Hacerlo bien ahora ahorra horas de confusión después.

```
wow_ah_lab/
│
├── config/
│   ├── config.py          # configuración general (region, realm_id, etc.)
│   └── secrets.py         # credenciales API y DB (NUNCA subas esto a GitHub)
│
├── data/
│   └── raw/               # CSVs de respaldo opcionales
│
├── db/
│   ├── schema.sql         # el SQL para crear tus tablas
│   └── db_connection.py   # función para conectarse a MySQL
│
├── collectors/
│   ├── blizzard_auth.py   # obtener y renovar el access token
│   └── ah_collector.py    # descargar datos del AH
│
├── analysis/
│   ├── price_metrics.py   # calcular precio promedio, mediana, etc.
│   ├── volatility.py      # calcular volatilidad de precios
│   └── flip_finder.py     # detectar oportunidades de flip
│
├── reports/
│   └── daily_report.py    # generar reporte diario
│
├── scripts/
│   ├── run_collector.py   # script principal que corre el collector
│   └── run_analysis.py    # script principal que corre el análisis
│
├── tests/
│   └── test_api.py        # tus scripts de prueba
│
├── requirements.txt       # lista de librerías Python necesarias
└── README.md              # documentación de tu proyecto
```

**¿Por qué esta estructura?**

Cada carpeta tiene una responsabilidad clara. Si algo falla, sabés exactamente dónde mirar. Si querés agregar una feature nueva (ej: análisis de crafting), sabés dónde ponerla sin romper lo existente.

---

## 7. Diseño de Base de Datos

### Principio: Diseñar para las preguntas que vas a hacer

Antes de diseñar tablas, pensá en las preguntas que vas a querer responder:

- "¿Cuál fue el precio mínimo de Flask of Power el lunes de las últimas 4 semanas?"
- "¿Qué items tuvieron la mayor volatilidad de precio en las últimas 72 horas?"
- "¿Cuántos listings de item X había hace 6 horas vs ahora?"

Con esas preguntas en mente, diseñamos estas tablas:

```sql
-- Archivo: db/schema.sql
-- Ejecutá esto una sola vez para crear tu base de datos

CREATE DATABASE IF NOT EXISTS wow_ah_lab;
USE wow_ah_lab;

-- ============================================
-- TABLA: items
-- Catálogo de items que monitoreamos
-- ============================================
CREATE TABLE IF NOT EXISTS items (
    item_id         INT PRIMARY KEY,        -- ID de Blizzard (ej: 191501)
    name            VARCHAR(200) NOT NULL,  -- nombre legible (ej: "Flask of Power")
    category        VARCHAR(50),            -- flask, potion, herb, ore, etc.
    subcategory     VARCHAR(50),            -- nivel de granularidad extra
    is_monitored    BOOLEAN DEFAULT TRUE,   -- para filtrar solo los que nos interesan
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: realms
-- Los servidores que monitoreamos
-- ============================================
CREATE TABLE IF NOT EXISTS realms (
    realm_id        INT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,  -- ej: "Stormrage"
    region          VARCHAR(5) NOT NULL,    -- us, eu, kr, tw
    timezone        VARCHAR(50)             -- para calcular reset day correctamente
);

-- ============================================
-- TABLA: ah_snapshots
-- Cada fila = una "foto" del AH en un momento dado
-- Esta es la tabla más importante
-- ============================================
CREATE TABLE IF NOT EXISTS ah_snapshots (
    snapshot_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- ¿De qué item y servidor?
    item_id         INT NOT NULL,
    realm_id        INT NOT NULL,
    
    -- ¿Cuándo se capturó?
    captured_at     TIMESTAMP NOT NULL,
    
    -- Métricas del snapshot
    min_price       DECIMAL(15,2),  -- precio mínimo en gold (ya convertido de cobre)
    max_price       DECIMAL(15,2),  -- precio máximo
    avg_price       DECIMAL(15,2),  -- precio promedio ponderado por cantidad
    median_price    DECIMAL(15,2),  -- mediana de precios
    total_quantity  INT,            -- cantidad total de unidades disponibles
    listing_count   INT,            -- número de listings (stacks) distintos
    
    -- Índices para consultas rápidas
    INDEX idx_item_time (item_id, captured_at),
    INDEX idx_realm_time (realm_id, captured_at),
    INDEX idx_captured_at (captured_at),
    
    -- Relaciones
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    FOREIGN KEY (realm_id) REFERENCES realms(realm_id)
);

-- ============================================
-- TABLA: raw_listings (opcional pero muy útil)
-- Guardamos los listings individuales para análisis profundo
-- CUIDADO: esta tabla crece MUY rápido. Considerar solo para items prioritarios.
-- ============================================
CREATE TABLE IF NOT EXISTS raw_listings (
    listing_id      BIGINT PRIMARY KEY,     -- el ID que da Blizzard
    item_id         INT NOT NULL,
    realm_id        INT NOT NULL,
    captured_at     TIMESTAMP NOT NULL,
    
    price_per_unit  DECIMAL(15,2) NOT NULL, -- precio por unidad en gold
    quantity        INT NOT NULL,
    time_left       ENUM('SHORT', 'MEDIUM', 'LONG', 'VERY_LONG'),
    
    INDEX idx_item_captured (item_id, captured_at),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

-- ============================================
-- TABLA: patch_events
-- Registro manual de parches para correlacionar con precios
-- ============================================
CREATE TABLE IF NOT EXISTS patch_events (
    event_id        INT AUTO_INCREMENT PRIMARY KEY,
    patch_version   VARCHAR(20),          -- ej: "11.0.5"
    event_type      VARCHAR(50),          -- new_raid, new_season, hotfix, etc.
    event_date      DATE NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Poblar el catálogo de items

Después de crear las tablas, necesitás cargar los items que vas a monitorear. Ejemplo básico:

```sql
-- Insertar tu realm
INSERT INTO realms VALUES (1136, 'Stormrage', 'us', 'America/New_York');

-- Insertar items de ejemplo (Flasks de The War Within)
-- Los item_id los encontrás buscando el item en wowhead.com
INSERT INTO items (item_id, name, category, subcategory) VALUES
(191499, 'Flask of Alchemical Chaos', 'consumable', 'flask'),
(191500, 'Flask of Crystallized Speed', 'consumable', 'flask'),
(191501, 'Flask of Tempered Aggression', 'consumable', 'flask'),
(201399, 'Iced Phial of Corrupting Rage', 'consumable', 'phial'),
-- Herbs
(191384, 'Hochenblume', 'material', 'herb'),
(191385, 'Saxifrage', 'material', 'herb'),
(191386, 'Writhebark', 'material', 'herb');
```

---

## 8. Insertar Datos en MySQL desde Python

### Conectar Python con MySQL

Primero instalás la librería:

```bash
pip install mysql-connector-python
```

Luego creás tu módulo de conexión:

```python
# db/db_connection.py

import mysql.connector
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
```

```python
# config/secrets.py
# IMPORTANTE: Agregá este archivo a .gitignore para no subir credenciales

CLIENT_ID = "tu_client_id_de_blizzard"
CLIENT_SECRET = "tu_client_secret_de_blizzard"

DB_HOST = "localhost"  # en PythonAnywhere será diferente
DB_USER = "tu_usuario_mysql"
DB_PASSWORD = "tu_password_mysql"
DB_NAME = "wow_ah_lab"
```

### El script collector completo

```python
# collectors/ah_collector.py

import requests
import mysql.connector
from datetime import datetime
from config.secrets import CLIENT_ID, CLIENT_SECRET, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from config.config import REGION, REALM_ID

def get_access_token():
    """Obtiene token de acceso de Blizzard."""
    url = f"https://{REGION}.battle.net/oauth/token"
    response = requests.post(
        url,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"}
    )
    response.raise_for_status()  # lanza error si hay problema
    return response.json()["access_token"]

def get_ah_data(realm_id, token):
    """Descarga todos los auctions del AH."""
    url = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{realm_id}/auctions"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params={"namespace": f"dynamic-{REGION}", "locale": "en_US"}
    )
    response.raise_for_status()
    return response.json().get("auctions", [])

def get_monitored_items(cursor):
    """Obtiene la lista de items que queremos monitorear."""
    cursor.execute("SELECT item_id FROM items WHERE is_monitored = TRUE")
    return {row[0] for row in cursor.fetchall()}  # set para búsquedas O(1)

def calculate_metrics(listings):
    """
    Dado un listado de auctions para UN item específico,
    calcula las métricas agregadas.
    
    listings: lista de dicts con keys 'price_per_unit' y 'quantity'
    """
    if not listings:
        return None
    
    # Ordenamos por precio para calcular mínimo/máximo/mediana
    prices = sorted(listings, key=lambda x: x['price_per_unit'])
    
    min_price = prices[0]['price_per_unit']
    max_price = prices[-1]['price_per_unit']
    
    # Precio promedio ponderado por cantidad
    total_value = sum(l['price_per_unit'] * l['quantity'] for l in listings)
    total_qty = sum(l['quantity'] for l in listings)
    avg_price = total_value / total_qty if total_qty > 0 else 0
    
    # Mediana (valor del medio en la lista ordenada por precio)
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

def save_snapshots(cursor, snapshots, realm_id):
    """Inserta los snapshots en la base de datos."""
    
    # Preparamos el INSERT statement
    # %s son placeholders para los valores (evita SQL injection)
    insert_query = """
        INSERT INTO ah_snapshots 
        (item_id, realm_id, captured_at, min_price, max_price, avg_price, 
         median_price, total_quantity, listing_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    captured_at = datetime.now()
    rows_inserted = 0
    
    for item_id, metrics in snapshots.items():
        values = (
            item_id,
            realm_id,
            captured_at,
            metrics['min_price'],
            metrics['max_price'],
            metrics['avg_price'],
            metrics['median_price'],
            metrics['total_quantity'],
            metrics['listing_count']
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
            password=DB_PASSWORD, database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)  # devuelve dicts en lugar de tuplas
        print("✅ Conectado a MySQL")
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return
    
    # 2. Obtener items monitoreados
    monitored_items = get_monitored_items(cursor)
    print(f"📋 Monitoreando {len(monitored_items)} items")
    
    # 3. Obtener token de Blizzard
    try:
        token = get_access_token()
        print("✅ Token de Blizzard obtenido")
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        conn.close()
        return
    
    # 4. Descargar datos del AH
    try:
        all_auctions = get_ah_data(REALM_ID, token)
        print(f"✅ Descargados {len(all_auctions)} listings del AH")
    except Exception as e:
        print(f"❌ Error descargando AH: {e}")
        conn.close()
        return
    
    # 5. Filtrar y agrupar por item
    # Queremos: { item_id: [lista de listings de ese item] }
    items_data = {}
    for auction in all_auctions:
        item_id = auction.get("item", {}).get("id")
        
        # Solo procesamos items que estamos monitoreando
        if item_id not in monitored_items:
            continue
        
        # Convertimos de cobre a gold
        buyout = auction.get("buyout", 0)
        quantity = auction.get("quantity", 1)
        
        if buyout == 0:  # algunos items solo tienen bid, no buyout
            continue
        
        price_per_unit = (buyout / quantity) / 10000  # cobre → gold
        
        if item_id not in items_data:
            items_data[item_id] = []
        
        items_data[item_id].append({
            'price_per_unit': price_per_unit,
            'quantity': quantity
        })
    
    print(f"📊 Items con listings activos: {len(items_data)}")
    
    # 6. Calcular métricas por item
    snapshots = {}
    for item_id, listings in items_data.items():
        metrics = calculate_metrics(listings)
        if metrics:
            snapshots[item_id] = metrics
    
    # 7. Guardar en MySQL
    rows = save_snapshots(cursor, snapshots, REALM_ID)
    conn.commit()  # IMPORTANTE: el commit hace que los cambios sean permanentes
    
    print(f"✅ Guardados {rows} snapshots en MySQL")
    
    # 8. Cerrar conexión
    cursor.close()
    conn.close()
    print(f"[{datetime.now()}] Colección completada.\n")

if __name__ == "__main__":
    run_collection()
```

### Consultar datos desde Python

```python
# Ejemplo: obtener historial de precios de un item
def get_price_history(item_id, days=7):
    """Obtiene el historial de precio mínimo de un item."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            captured_at,
            min_price,
            avg_price,
            median_price,
            total_quantity,
            listing_count
        FROM ah_snapshots
        WHERE item_id = %s
          AND captured_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        ORDER BY captured_at ASC
    """
    
    cursor.execute(query, (item_id, days))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results

# Uso:
history = get_price_history(191501, days=7)
for row in history:
    print(f"{row['captured_at']}: {row['min_price']}g (vol: {row['total_quantity']})")
```

---

## 9. PythonAnywhere Paso a Paso

### Paso 1: Crear cuenta

1. Andá a https://www.pythonanywhere.com
2. Registrate (la cuenta gratuita alcanza para empezar).
3. La cuenta gratuita incluye: 1 tarea programada diaria, acceso a MySQL, consola Bash.

**Nota sobre el plan gratuito**: Solo permite 1 tarea al día. Para capturar datos cada 4 horas necesitarás el plan "Hacker" (~$5/mes). Igual empezá gratis para aprender.

### Paso 2: Subir tu código

**Opción A: Via Git (recomendada)**

1. Desde la consola de PythonAnywhere, corré:
   ```bash
   git clone https://github.com/tu_usuario/wow_ah_lab.git
   ```

**Opción B: Subir archivos manualmente**

1. Andá a "Files" en el dashboard.
2. Creá la carpeta `wow_ah_lab`.
3. Subí tus archivos uno por uno.

### Paso 3: Configurar la base de datos MySQL

1. En el dashboard, andá a **"Databases"**.
2. Hacé click en "Initialize MySQL".
3. Ponés una contraseña para tu usuario MySQL.
4. PythonAnywhere te muestra el **host** de tu DB (algo como `tu_usuario.mysql.pythonanywhere-services.com`).
5. Anotás: host, usuario, password, y el nombre de la DB (generalmente `tu_usuario$nombre_db`).

Para crear las tablas:
1. Click en el link de tu base de datos en el dashboard.
2. Se abre un cliente MySQL web.
3. Copiás y pegás el contenido de tu `db/schema.sql` y lo ejecutás.

### Paso 4: Actualizar secrets.py para PythonAnywhere

En PythonAnywhere, tu `config/secrets.py` debe usar los datos reales:

```python
# En PythonAnywhere, el host de MySQL es diferente
DB_HOST = "tu_usuario.mysql.pythonanywhere-services.com"
DB_USER = "tu_usuario"
DB_PASSWORD = "la_contraseña_que_pusiste"
DB_NAME = "tu_usuario$wow_ah_lab"  # nota el símbolo $ en el nombre
```

### Paso 5: Instalar dependencias

En la consola Bash de PythonAnywhere:

```bash
pip install --user requests mysql-connector-python
```

### Paso 6: Configurar el Cron Job

1. En el dashboard, andá a **"Tasks"** (o "Scheduled Tasks").
2. Click en "Add a new scheduled task".
3. Configurás:
   - **Hour**: el horario en UTC (PythonAnywhere usa UTC)
   - **Command**: `python /home/tu_usuario/wow_ah_lab/scripts/run_collector.py`
4. En el plan gratuito, podés configurar 1 tarea diaria a una hora específica.

### Paso 7: Verificar que funciona

1. Desde la consola, corré el script manualmente primero:
   ```bash
   cd ~/wow_ah_lab
   python scripts/run_collector.py
   ```
2. Verificá que no hay errores.
3. Chequeá en MySQL que los datos se guardaron:
   ```sql
   SELECT COUNT(*) FROM ah_snapshots;
   SELECT * FROM ah_snapshots ORDER BY captured_at DESC LIMIT 5;
   ```

### Tips de PythonAnywhere

- Los logs de tus cron jobs los podés ver en la sección "Tasks".
- Si un script falla silenciosamente, agregá logging a un archivo: `logging.basicConfig(filename='/home/tu_usuario/wow_ah_lab/app.log', level=logging.INFO)`.
- La consola de MySQL en el dashboard es muy útil para verificar datos rápidamente.

---

## 10. Fases Evolutivas del Proyecto

### Fase 0 — Prueba de concepto (Semana 1-2)
**Objetivo**: Ver datos reales del AH en tu terminal.

- [ ] Crear cuenta de desarrollador en Blizzard
- [ ] Autenticarse con la API
- [ ] Descargar y printear datos del AH
- [ ] Entender la estructura del JSON

**Criterio de éxito**: Podés correr un script y ver listings reales en la consola.

### Fase 1 — Colección básica (Semana 3-5)
**Objetivo**: Guardar snapshots automáticamente en MySQL.

- [ ] Diseñar y crear tablas en MySQL
- [ ] Escribir el collector completo
- [ ] Filtrar por items monitoreados
- [ ] Calcular métricas básicas (min, max, avg)
- [ ] Guardar en MySQL
- [ ] Desplegar en PythonAnywhere con cron job diario

**Criterio de éxito**: Cada día tenés nuevas filas en tu tabla `ah_snapshots`.

### Fase 2 — Análisis histórico (Semana 6-9)
**Objetivo**: Ver tendencias de precio a lo largo del tiempo.

- [ ] Script de análisis que lee la DB
- [ ] Calcular volatilidad (desvío estándar de precios)
- [ ] Detectar patrones semanales (precio lunes vs viernes)
- [ ] Generar reporte CSV o HTML simple
- [ ] Aumentar frecuencia de colección a cada 4-6 horas

**Criterio de éxito**: Podés responder "¿qué día de la semana es más barato este Flask?"

### Fase 3 — Detección de oportunidades (Semana 10-14)
**Objetivo**: Sistema que identifica flips rentables automáticamente.

- [ ] Definir métricas de flip (spread entre precio actual y precio promedio histórico)
- [ ] Algoritmo de scoring de oportunidades
- [ ] Sistema de alertas (email o archivo de texto con oportunidades del día)
- [ ] Análisis de correlación entre items (ej: Herbs → Flasks)
- [ ] Seguimiento de parches y su impacto

**Criterio de éxito**: El sistema te dice cada mañana "considera comprar X porque está 25% más barato que su promedio de 30 días".

### Fase 4 — Laboratorio avanzado (Mes 4+)
**Objetivo**: Modelos más sofisticados y visualización.

- [ ] Modelos de series de tiempo (predicción de precios)
- [ ] Dashboard web simple con Flask/Streamlit
- [ ] Análisis de crafting (¿conviene craftear o comprar?)
- [ ] Backtesting de estrategias pasadas
- [ ] Análisis multi-realm

---

## 11. Calendario Semanal: La Receta

### Semana 1 — "Hola, API"
**Tiempo estimado**: 3-4 horas total

**Día 1 (1h)**: Crear cuenta developer en Blizzard. Leer la documentación de la API (https://develop.battle.net/documentation/world-of-warcraft). Instalar Python y las librerías (`pip install requests`).

**Día 2 (1h)**: Escribir y correr el script de autenticación. Obtener tu primer access token. Celebrar el primer contacto real con una API.

**Día 3 (1.5h)**: Descargar datos del AH. Entender la estructura del JSON. Imprimir los datos y leerlos.

**Fin de semana (30min)**: Reflexionar qué datos ves y qué queries te gustaría hacerle.

### Semana 2 — "Hola, MySQL"
**Tiempo estimado**: 4-5 horas total

**Día 1 (1h)**: Instalar MySQL localmente. Instalar `mysql-connector-python`. Entender qué es una base de datos relacional.

**Día 2 (1.5h)**: Crear tu base de datos y tablas usando el schema provisto. Insertar algunos datos de prueba manualmente.

**Día 3 (2h)**: Escribir el script que conecta Python con MySQL. Insertar los primeros datos reales del AH.

### Semana 3 — "El Collector Funciona"
**Tiempo estimado**: 4-5 horas total

**Día 1-2 (3h)**: Escribir el collector completo. Incluye filtrado por items, conversión de precios, cálculo de métricas. Testearlo localmente.

**Día 3 (2h)**: Debuggear. Probablemente algo falle. Leer los errores, buscar la solución. Este proceso ES el aprendizaje.

### Semana 4 — "PythonAnywhere"
**Tiempo estimado**: 3-4 horas total

**Día 1 (1h)**: Crear cuenta en PythonAnywhere. Explorar el dashboard. Crear la DB en MySQL de PythonAnywhere.

**Día 2 (1.5h)**: Subir tu código. Instalar dependencias. Configurar secrets.py con los datos de PythonAnywhere.

**Día 3 (1.5h)**: Correr el collector manualmente en PythonAnywhere. Verificar que los datos lleguen a la DB. Configurar el cron job.

### Semana 5 — "Primera Semana de Datos"
**Objetivo**: No tocar nada. Dejar que el cron job corra y acumular datos.

**Tarea única**: Cada día, revisar que el cron job corrió y que hay nuevas filas en la DB. Tomar notas sobre el mercado en el juego.

### Semana 6-7 — "Análisis"
**Objetivo**: Hacer las primeras preguntas reales a los datos.

**Queries SQL para practicar**:
```sql
-- Precio mínimo de un item los últimos 7 días
SELECT DATE(captured_at) as fecha, MIN(min_price) as precio_minimo
FROM ah_snapshots
WHERE item_id = 191501
GROUP BY DATE(captured_at)
ORDER BY fecha;

-- ¿Qué item tuvo mayor volatilidad esta semana?
SELECT i.name, STDDEV(s.min_price) as volatilidad
FROM ah_snapshots s
JOIN items i ON s.item_id = i.item_id
WHERE s.captured_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY s.item_id, i.name
ORDER BY volatilidad DESC;
```

---

## 12. Qué Medir Primero y Por Qué

### El error clásico del principiante

Querer medir todo desde el día 1. No hagas eso. Empezá con lo que te enseña más con menos datos.

### Métricas de Fase 1 (las únicas que importan al principio)

**1. Precio mínimo (`min_price`)**

Es la métrica más directa. Representa el precio al que podés comprar ahora mismo. Es la señal más "limpia" porque es un dato objetivo, sin ponderación.

*¿Por qué no el promedio?* El promedio puede estar inflado por un vendedor loco que postea a 10x el precio de mercado. El mínimo te dice el precio real de compra.

**2. Precio promedio ponderado por volumen**

Divide el valor total del mercado por la cantidad total de unidades. Esto da un precio más representativo de "en qué rango está el mercado realmente".

```
avg_price = Σ(precio_i × cantidad_i) / Σ(cantidad_i)
```

**3. Volumen total (`total_quantity`)**

Cuántas unidades hay en el AH en este momento. Bajo volumen = mercado ilíquido = precios más volátiles = oportunidades y riesgos.

**4. Número de listings (`listing_count`)**

Cuántos vendedores distintos hay. Si hay 200 unidades pero solo 2 listings, eso es diferente a 200 unidades en 50 listings. Muchos listings pequeños = mercado competitivo y saludable.

### Métricas de Fase 2 (cuando tengas 2+ semanas de datos)

**5. Volatilidad (desvío estándar del precio mínimo)**

```python
import statistics
volatility = statistics.stdev([snapshot['min_price'] for snapshot in history])
```

Un item con alta volatilidad tiene precios que saltan mucho. Eso puede ser bueno (oportunidades de compra barata) o malo (riesgo de quedarte con stock caro).

**6. Precio percentil 10 histórico**

El precio al que históricamente el item estuvo "muy barato". Si el precio actual está por debajo de este valor, es señal de compra.

```python
import numpy as np
p10 = np.percentile([s['min_price'] for s in history], 10)
```

**7. Spread entre precio actual y media de 7 días**

```python
spread_pct = (current_min - avg_7days) / avg_7days * 100
# Si spread_pct < -20%: el precio actual está 20% por debajo del promedio = posible oportunidad
```

---

## 13. Riesgos Conceptuales

### Riesgo 1: Confundir datos con señales

Un precio bajo no significa automáticamente "comprar". Puede significar que el item tiene menos demanda, que salió contenido que lo hizo obsoleto, o que el mercado está inundado de bots.

**Solución**: Siempre combinar datos de precio con contexto del juego. Tu conocimiento como jugador es tan valioso como los datos.

### Riesgo 2: La trampa del survivorship bias en el catálogo

Si solo monitoreás los items que "creés" que son importantes, vas a perder oportunidades en items que no tenías en el radar.

**Solución**: En Fase 2, considerá monitorear TODOS los items del AH, no solo los preseleccionados.

### Riesgo 3: La API de Blizzard no es en tiempo real

La API del AH se actualiza cada ~1 hora. No podés hacer HFT (High Frequency Trading) en el AH de WoW via API.

**Solución**: Diseñar estrategias que funcionen con esa latencia. Las oportunidades de 4-6 horas son perfectamente capturables.

### Riesgo 4: Los precios en el AH están manipulados

Hay jugadores que deliberadamente inflan precios postando a valores absurdos para distorsionar los datos de addons como TSM.

**Solución**: Al calcular promedios, filtrar outliers estadísticos. Precio > 3 desvíos estándar de la media = outlier = excluir del cálculo.

```python
def filter_outliers(listings, sigma=3):
    prices = [l['price_per_unit'] for l in listings]
    mean = sum(prices) / len(prices)
    std = statistics.stdev(prices) if len(prices) > 1 else 0
    
    return [l for l in listings 
            if abs(l['price_per_unit'] - mean) <= sigma * std]
```

### Riesgo 5: Sobreajustar al pasado reciente

Si ves que un item bajó de precio y lo comprás masivamente esperando que suba, pero la razón de la baja fue un cambio de balance que lo hizo menos útil, te vas a quedar con stock que no podés vender.

**Solución**: Antes de cualquier compra grande, verificar si hubo hotfixes o cambios de balance recientes.

### Riesgo 6: La ilusión de precisión

Calcular el precio con 8 decimales cuando el spread de mercado es de 10 gold no agrega valor. La precisión falsa genera confianza falsa.

**Solución**: Redondear siempre a 2 decimales en gold. El market noise absorbe cualquier diferencia menor.

### Riesgo 7: El costo de oportunidad del tiempo

Tiempo que pasás mirando datos = tiempo que no pasás jugando. Si el proyecto se convierte en trabajo, dejás de disfrutarlo.

**Solución**: Automatizar al máximo posible. El objetivo es que el sistema trabaje por vos, no que vos trabajes para el sistema.

---

## 14. Estrategia Goblin: La Perspectiva del Experto

### Principio 1: El AH es un juego de información asimétrica

Vos tenés datos históricos. El 95% de los jugadores no. Eso ya es una ventaja enorme. No necesitás estrategias complicadas para ganar; solo necesitás más información que tu contraparte.

### Principio 2: Seguí el ciclo, no el precio

El precio es un síntoma. El ciclo es la causa. Si es lunes antes del reset, los precios de consumibles van a subir mañana sin importar dónde estén hoy. No necesitás análisis complejo para eso.

### Las 3 estrategias más rentables para empezar

**Estrategia A: Reset Day Arbitrage**

*Cómo funciona*: Los jueves y viernes, después del reset, los precios de consumibles caen porque la demanda raid se satisfizo. Comprás en ese valle y vendés el lunes/martes antes del próximo reset.

*Requiere*: 2-3 semanas de datos para identificar el patrón en tu servidor específico.

*Capital mínimo*: 5,000-10,000 gold para ser relevante.

*Riesgo*: Bajo, porque el ciclo es estructural y predecible.

**Estrategia B: Patch Speculation**

*Cómo funciona*: Cuando se anuncia un parche nuevo en el PTR (Public Test Realm), comprás materiales que se van a necesitar para el nuevo contenido antes de que el precio suba.

*Requiere*: Saber leer las notas de PTR. Entender qué materials va a demandar el nuevo contenido.

*Ejemplo concreto*: Si el PTR muestra un nuevo Flask que requiere Herb X, comprás Herb X antes de que salga el parche.

*Riesgo*: Medio. Los parches se pueden retrasarse o cambiar antes de salir.

**Estrategia C: Supply Shock Exploitation**

*Cómo funciona*: Cuando Blizzard hace un baneo masivo de bots, la oferta de mats cae súbitamente y los precios suben. Si tenés stock de esos mats, vendés en ese pico.

*Requiere*: Mantener stock de los mats más farmeados por bots (herbs y ores principalmente). Monitorear foros como r/woweconomy para detectar noticias de baneos.

*Riesgo*: Medio. Si el baneo no sucede, tu capital está inmovilizado en mats.

### Principio 3: Especialización > Diversificación (al principio)

Intentar dominar todos los mercados a la vez es una receta para perder foco. Elegí 1 categoría, entendela profundamente, extraé el máximo valor de ella, y luego expandí.

*Recomendación para empezar*: **Flasks y Phials**. Son el mercado de consumibles más grande y predecible. Tienen alta rotación, ciclo semanal claro, y correlación directa con el calendario de raids.

### Principio 4: El mejor addon + tu sistema

TradeSkillMaster (TSM) es el addon que usan todos los goblins serios. Tu sistema cuantitativo NO reemplaza a TSM; lo complementa. TSM te ayuda a ejecutar en el juego (posta automática, buyout rápido). Tu sistema te dice qué comprar y cuándo.

### Una advertencia importante

El AH de WoW es entretenimiento, no inversión real. No tomes riesgos de capital que te generen estrés. El objetivo es disfrutar el proceso y aprender. El oro es solo el scorecard.

---

## 🗺️ Resumen Ejecutivo: Por Dónde Empezar Mañana

1. Creá la cuenta de desarrollador en https://develop.battle.net (15 min).
2. Instalá Python y `pip install requests mysql-connector-python` (10 min).
3. Copiá el script `test_api.py` de la sección 5, reemplazá tus credenciales y correlo (20 min).
4. Cuando veas datos reales en tu terminal, ya sos un desarrollador que consume APIs.

El resto viene solo, paso a paso.

---

*"In this world, Goldsink, you either flip or you get flipped."*
*— Ningún NPC de WoW, pero debería haberlo dicho.*
