BEGIN;

INSERT INTO plans (name)
VALUES
    ('admin'),
    ('moderator'),
    ('customer'),
    ('performer');

COMMIT;
