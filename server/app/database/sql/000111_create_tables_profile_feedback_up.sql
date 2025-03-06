BEGIN;

CREATE TABLE IF NOT EXISTS users_profile_feedbacks (
	id SERIAL PRIMARY KEY,
	content VARCHAR(2000),
	rate SMALLINT CHECK (rate BETWEEN 0 AND 5) DEFAULT 0,
	commentator_id INTEGER,
	profile_id INTEGER NOT NULL,
	FOREIGN KEY (commentator_id) REFERENCES users(id) ON DELETE SET NULL,
	FOREIGN KEY (profile_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS profile_feedbacks_images (
	id SERIAL PRIMARY KEY,
	image_link VARCHAR(256),
	profile_feedback_id INTEGER NOT NULL,
	FOREIGN KEY (profile_feedback_id) REFERENCES users_profile_feedbacks(id) ON DELETE CASCADE
);

COMMIT;
