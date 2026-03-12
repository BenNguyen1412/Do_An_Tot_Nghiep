-- Ensure status field in bookings table has proper constraints
-- This prevents NULL values in the future

-- First, ensure all NULL values are fixed (already done in previous migration)
UPDATE bookings 
SET status = 'pending'
WHERE status IS NULL;

-- Add NOT NULL constraint and set default
ALTER TABLE bookings 
ALTER COLUMN status SET DEFAULT 'pending';

ALTER TABLE bookings 
ALTER COLUMN status SET NOT NULL;

-- Verify
SELECT COUNT(*) as total_bookings,
       COUNT(status) as bookings_with_status,
       COUNT(*) FILTER (WHERE status IS NULL) as null_status_count
FROM bookings;

COMMENT ON COLUMN bookings.status IS 'Legacy booking status (NOT NULL, default: pending): pending, active, confirmed, completed, cancelled';

SELECT 'Migration completed: status field now has NOT NULL constraint and default value' as result;
