CREATE TABLE ifc_models (
  id SERIAL PRIMARY KEY,
  filename VARCHAR NOT NULL,
  uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE TABLE distribution_systems (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  predefined_type VARCHAR
);

CREATE TABLE classification_mappings (
  id SERIAL PRIMARY KEY,
  ifc_class VARCHAR NOT NULL,
  predefined_type VARCHAR,
  target_category VARCHAR NOT NULL,
  bac_twin_code VARCHAR,
  amev_code VARCHAR
);

CREATE TABLE hvac_components (
  id SERIAL PRIMARY KEY,
  global_id VARCHAR UNIQUE NOT NULL,
  name VARCHAR,
  ifc_class VARCHAR NOT NULL,
  object_type VARCHAR,
  properties JSON,
  model_id INTEGER REFERENCES ifc_models(id) ON DELETE CASCADE,
  system_id INTEGER REFERENCES distribution_systems(id) ON DELETE SET NULL,
  mapping_id INTEGER REFERENCES classification_mappings(id) ON DELETE SET NULL
);