-- Migration: Add VietQR Payment Fields to Bookings Table
-- Purpose: Track VietQR payments and auto-verification

-- Add payment-related columns
ALTER TABLE bookings 
ADD COLUMN IF NOT EXISTS total_hours NUMERIC(4, 2),
ADD COLUMN IF NOT EXISTS total_price NUMERIC(10, 2), 
ADD COLUMN IF NOT EXISTS customer_email VARCHAR(100),
ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20) DEFAULT 'vietqr',
ADD COLUMN IF NOT EXISTS payment_status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS booking_status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS qr_code_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS bank_transaction_id VARCHAR(200),
ADD COLUMN IF NOT EXISTS payment_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS payment_note TEXT;

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS idx_bookings_payment_status ON bookings(payment_status);
CREATE INDEX IF NOT EXISTS idx_bookings_booking_status ON bookings(booking_status);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_bank_transaction ON bookings(bank_transaction_id) WHERE bank_transaction_id IS NOT NULL;

-- Update existing data with default values
UPDATE bookings 
SET 
    total_hours = 1.0,
    total_price = 100000,
    payment_status = 'paid',
    booking_status = 'confirmed',
    payment_method = 'cash'
WHERE total_hours IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN bookings.payment_method IS 'Payment method: vietqr, cash';
COMMENT ON COLUMN bookings.payment_status IS 'Payment status: pending, verifying, paid, failed, refunded';
COMMENT ON COLUMN bookings.booking_status IS 'Booking status: pending, confirmed, active, completed, cancelled';
COMMENT ON COLUMN bookings.qr_code_url IS 'VietQR image URL for payment';
COMMENT ON COLUMN bookings.bank_transaction_id IS 'Bank transaction reference for auto-verification';
COMMENT ON COLUMN bookings.payment_verified_at IS 'Timestamp when payment was verified';

SELECT 'VietQR payment migration completed successfully!' AS status;
