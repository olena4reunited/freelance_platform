BEGIN;

ALTER TABLE orders 
ADD COLUMN execution_type VARCHAR(6)
DEFAULT 'single';

ALTER TABLE orders
ADD CONSTRAINT matching_execution_type
CHECK (
    (execution_type = 'single' AND performer_team_id IS NULL)
    OR 
    (execution_type = 'team' AND performer_id IS NULL)
);

COMMIT;
