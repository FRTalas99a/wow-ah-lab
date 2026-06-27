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