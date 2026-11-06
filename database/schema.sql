-- Gold AI: fresh MySQL database only. Select an empty database before executing.
-- Generated from unified SQLAlchemy models; no destructive statements or seeded credentials.



CREATE TABLE gold_types (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	code VARCHAR(50) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	unit VARCHAR(30) NOT NULL, 
	source VARCHAR(100), 
	PRIMARY KEY (id), 
	UNIQUE (code)
)

;


CREATE TABLE ml_models (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	algorithm VARCHAR(30) NOT NULL, 
	version VARCHAR(20) NOT NULL, 
	artifact_path VARCHAR(255) NOT NULL, 
	metrics JSON, 
	is_active BOOL NOT NULL, 
	trained_at DATETIME, 
	PRIMARY KEY (id)
)

;


CREATE TABLE users (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	username VARCHAR(50), 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	full_name VARCHAR(100), 
	`role` VARCHAR(10) NOT NULL, 
	is_active BOOL NOT NULL, 
	created_at DATETIME NOT NULL DEFAULT now(), 
	PRIMARY KEY (id), 
	UNIQUE (email)
)

;

CREATE UNIQUE INDEX ix_users_username ON users (username);


CREATE TABLE gold_prices (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	gold_type_id INTEGER NOT NULL, 
	date DATE NOT NULL, 
	open NUMERIC(20, 4) NOT NULL, 
	high NUMERIC(20, 4) NOT NULL, 
	low NUMERIC(20, 4) NOT NULL, 
	close NUMERIC(20, 4) NOT NULL, 
	volume NUMERIC(20, 4), 
	buy NUMERIC(20, 4), 
	sell NUMERIC(20, 4), 
	created_at DATETIME NOT NULL DEFAULT now(), 
	PRIMARY KEY (id), 
	CONSTRAINT uq_gold_prices_type_date UNIQUE (gold_type_id, date), 
	FOREIGN KEY(gold_type_id) REFERENCES gold_types (id)
)

;

CREATE INDEX ix_gold_prices_date ON gold_prices (date);


CREATE TABLE predictions (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	user_id INTEGER, 
	gold_type_id INTEGER NOT NULL, 
	ml_model_id INTEGER NOT NULL, 
	horizon_days INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(gold_type_id) REFERENCES gold_types (id), 
	FOREIGN KEY(ml_model_id) REFERENCES ml_models (id)
)

;

CREATE INDEX ix_predictions_user_id ON predictions (user_id);


CREATE TABLE prediction_items (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	prediction_id INTEGER NOT NULL, 
	target_date DATE NOT NULL, 
	predicted_price NUMERIC(20, 4) NOT NULL, 
	lower_bound NUMERIC(20, 4), 
	upper_bound NUMERIC(20, 4), 
	actual_price NUMERIC(20, 4), 
	PRIMARY KEY (id), 
	FOREIGN KEY(prediction_id) REFERENCES predictions (id)
)

;

CREATE INDEX ix_prediction_items_prediction_id ON prediction_items (prediction_id);
