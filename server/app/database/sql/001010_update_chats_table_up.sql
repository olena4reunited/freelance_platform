BEGIN;

CREATE TABLE IF NOT EXISTS chats_users (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (chat_id, user_id)
);

INSERT INTO chat_users (chat_id, user_id)
SELECT id, user_one_id FROM chats
UNION
SELECT id, user_two_id FROM chats;

ALTER TABLE chats 
DROP COLUMN user_one_id,
DROP COLUMN user_two_id;

COMMIT;
