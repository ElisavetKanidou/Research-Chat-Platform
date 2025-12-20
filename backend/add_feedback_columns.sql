-- Add feedback columns to chat_messages table
-- Run this in pgAdmin4 Query Tool

-- Check existing columns (optional - just to see current state)
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'chat_messages'
ORDER BY ordinal_position;

-- Add user_feedback column if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'chat_messages'
        AND column_name = 'user_feedback'
    ) THEN
        ALTER TABLE chat_messages
        ADD COLUMN user_feedback BOOLEAN DEFAULT NULL;

        RAISE NOTICE 'user_feedback column added successfully!';
    ELSE
        RAISE NOTICE 'user_feedback column already exists';
    END IF;
END $$;

-- Add feedback_timestamp column if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'chat_messages'
        AND column_name = 'feedback_timestamp'
    ) THEN
        ALTER TABLE chat_messages
        ADD COLUMN feedback_timestamp TIMESTAMP DEFAULT NULL;

        RAISE NOTICE 'feedback_timestamp column added successfully!';
    ELSE
        RAISE NOTICE 'feedback_timestamp column already exists';
    END IF;
END $$;

-- Verify the columns were added
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'chat_messages'
AND column_name IN ('user_feedback', 'feedback_timestamp');

-- Show success message
SELECT '✅ Migration completed! The feedback columns have been added to chat_messages table.' AS status;
