-- Fix NULL status values in bookings table
-- Update bookings with NULL status based on payment status

-- For bookings with paid payment status, set status to 'completed' or 'confirmed'
UPDATE bookings 
SET status = CASE 
    WHEN payment_status = 'paid' THEN 'confirmed'
    WHEN payment_status = 'pending' THEN 'pending'
    WHEN payment_status = 'failed' THEN 'cancelled'
    ELSE 'active'
END
WHERE status IS NULL;

-- Show results
SELECT 
    payment_status,
    status,
    COUNT(*) as count
FROM bookings
GROUP BY payment_status, status
ORDER BY payment_status, status;

COMMENT ON COLUMN bookings.status IS 'Legacy status field: pending, active, confirmed, completed, cancelled';
