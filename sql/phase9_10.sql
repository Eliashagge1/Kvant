CREATE TABLE IF NOT EXISTS predictions(prediction_id VARCHAR PRIMARY KEY,model_version VARCHAR NOT NULL,symbol VARCHAR NOT NULL,made_at TIMESTAMP NOT NULL,resolve_after TIMESTAMP NOT NULL,prediction DOUBLE NOT NULL,lower_bound DOUBLE,upper_bound DOUBLE,features JSON NOT NULL,shadow BOOLEAN NOT NULL);
CREATE TABLE IF NOT EXISTS prediction_resolutions(prediction_id VARCHAR PRIMARY KEY,resolved_at TIMESTAMP NOT NULL,actual DOUBLE NOT NULL,error DOUBLE NOT NULL);
CREATE TABLE IF NOT EXISTS correction_events(timestamp TIMESTAMP NOT NULL,event_type VARCHAR NOT NULL,details JSON);
CREATE TABLE IF NOT EXISTS shadow_comparisons(timestamp TIMESTAMP NOT NULL,incumbent_version VARCHAR,candidate_version VARCHAR,incumbent_loss DOUBLE,candidate_loss DOUBLE);
CREATE TABLE IF NOT EXISTS paper_fills(order_id VARCHAR,symbol VARCHAR,timestamp TIMESTAMP,quantity DOUBLE,price DOUBLE,commission DOUBLE,impact DOUBLE);
CREATE TABLE IF NOT EXISTS live_backtest_divergence(timestamp TIMESTAMP,live_return DOUBLE,backtest_return DOUBLE,z_score DOUBLE);
