-- Postgres schema for multi-instance deployment
CREATE TABLE IF NOT EXISTS heal_status (
  id SERIAL PRIMARY KEY,
  run_id VARCHAR(255) NOT NULL,
  provider VARCHAR(64) NOT NULL,
  status VARCHAR(64) NOT NULL,
  logs TEXT,
  analysis JSONB,
  correlation_id VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_heal_status_run ON heal_status(run_id);
CREATE INDEX idx_heal_status_created ON heal_status(created_at DESC);

CREATE TABLE IF NOT EXISTS heal_audit (
  id SERIAL PRIMARY KEY,
  ts DOUBLE PRECISION NOT NULL,
  event VARCHAR(64) NOT NULL,
  run_id VARCHAR(255),
  provider VARCHAR(255),
  details JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_heal_audit_event ON heal_audit(event);
CREATE INDEX idx_heal_audit_ts ON heal_audit(ts DESC);

CREATE TABLE IF NOT EXISTS heal_tokens (
  id SERIAL PRIMARY KEY,
  run_id VARCHAR(255),
  model VARCHAR(128),
  input_tokens INT,
  output_tokens INT,
  correlation_id VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
