-- Add summary column if not exists
ALTER TABLE event_clusters ADD COLUMN IF NOT EXISTS summary TEXT;
