-- Add COMMENT_UPDATED to notificationtype enum
-- Run this SQL in your PostgreSQL database

ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'comment_updated';

-- Verify it was added
SELECT enum_range(NULL::notificationtype);
