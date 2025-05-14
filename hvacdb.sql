"""
Angepasste SQL-Struktur mit zusätzlichen Tabellen für Standorte und BAS-Codes
"""

-- Tabelle für IFC-Modelle
CREATE TABLE ifc_models (
  id SERIAL PRIMARY KEY,
  filename VARCHAR NOT NULL,
  uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Tabelle für Standortinformationen
CREATE TABLE locations (
  id SERIAL PRIMARY KEY,
  storey_id INTEGER,
  storey_name VARCHAR,
  space_id INTEGER,
  space_name VARCHAR
);

-- Tabelle für Verteilungssysteme
CREATE TABLE distribution_systems (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  predefined_type VARCHAR
);

-- Tabelle für Klassifizierungszuordnungen
CREATE TABLE classification_mappings (
  id SERIAL PRIMARY KEY,
  ifc_class VARCHAR NOT NULL,
  predefined_type VARCHAR,
  target_category VARCHAR NOT NULL,
  bac_twin_code VARCHAR,
  amev_code VARCHAR
);

-- Erweiterte Tabelle für HVAC-Komponenten
CREATE TABLE hvac_components (
  id SERIAL PRIMARY KEY,
  global_id VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  ifc_class VARCHAR NOT NULL,
  object_type VARCHAR,
  properties JSON,
  is_electronic BOOLEAN DEFAULT FALSE,
  bas_code VARCHAR,
  bas_standard VARCHAR,
  model_id INTEGER REFERENCES ifc_models(id) ON DELETE CASCADE,
  system_id INTEGER REFERENCES distribution_systems(id) ON DELETE SET NULL,
  mapping_id INTEGER REFERENCES classification_mappings(id) ON DELETE SET NULL,
  location_id INTEGER REFERENCES locations(id) ON DELETE SET NULL
);

-- Indizes für schnellere Abfragen
CREATE INDEX idx_hvac_components_model_id ON hvac_components(model_id);
CREATE INDEX idx_hvac_components_is_electronic ON hvac_components(is_electronic);
CREATE INDEX idx_hvac_components_ifc_class ON hvac_components(ifc_class);

-- Standard-Kategoriemappings einfügen
INSERT INTO classification_mappings (ifc_class, predefined_type, target_category, bac_twin_code, amev_code)
VALUES
  ('IfcFlowController', 'DAMPER', 'AIR_CONTROL_DAMPER', 'KHG01', 'REG01_ERH01_HZV'),
  ('IfcFlowController', 'VALVE', 'HEATING_VALVE', 'HEI01', 'HEI01_ERH01_HZV'),
  ('IfcFlowTerminal', 'AIRINLET', 'VENTILATION_INLET', 'LUE01', 'LTA01_ERH01_HZV'),
  ('IfcFlowTerminal', 'AIROUTLET', 'VENTILATION_OUTLET', 'LUE02', 'LTA02_ERH01_HZV'),
  ('IfcFlowMovingDevice', 'PUMP', 'CIRCULATION_PUMP', 'HEI02', 'HEI02_ERH01_HZV'),
  ('IfcFlowMovingDevice', 'FAN', 'VENTILATION_FAN', 'LUE03', 'LTA03_ERH01_HZV'),
  ('IfcEnergyConversionDevice', 'BOILER', 'HEATING_BOILER', 'HEI03', 'HEI03_ERH01_HZV'),
  ('IfcEnergyConversionDevice', 'HEATEXCHANGER', 'HEAT_EXCHANGER', 'KLI01', 'KLI01_ERH01_HZV'),
  ('IfcSensor', 'TEMPERATURESENSOR', 'TEMPERATURE_SENSOR', 'REG01', 'REG01_ERH01_HZV'),
  ('IfcActuator', NULL, 'ELECTRONIC_ACTUATOR', 'REG02', 'REG02_ERH01_HZV'),
  ('IfcController', NULL, 'CONTROL_UNIT', 'REG03', 'REG03_ERH01_HZV');

-- Standard-Verteilungssysteme einfügen
INSERT INTO distribution_systems (name, predefined_type)
VALUES
  ('Heizkreis', 'HEATING'),
  ('Lüftung KS', 'VENTILATION'),
  ('Warmwasser', 'DOMESTICHOTWATER'),
  ('Kältekreis', 'COOLING');