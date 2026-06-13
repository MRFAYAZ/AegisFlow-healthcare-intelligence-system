
One more thing: after the API starts working, create a proper Alembic migration later so the schema change is tracked.

For now, since you're trying to get the mini-project demo working, a direct:

ALTER TABLE facilities
ADD COLUMN contact_phone VARCHAR(20);

is the fastest path.