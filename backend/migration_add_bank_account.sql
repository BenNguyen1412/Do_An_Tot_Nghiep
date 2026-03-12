-- Migration: Add Bank Account Fields to Users Table
-- Purpose: Allow owners to store bank account info for receiving VietQR payments

-- Add bank account columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS bank_account_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS bank_account_name VARCHAR(200),
ADD COLUMN IF NOT EXISTS bank_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS bank_code VARCHAR(20);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_bank_account ON users(bank_account_number) WHERE bank_account_number IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN users.bank_account_number IS 'Bank account number for receiving VietQR payments';
COMMENT ON COLUMN users.bank_account_name IS 'Account holder name';
COMMENT ON COLUMN users.bank_name IS 'Bank name (e.g., Vietcombank, Techcombank)';
COMMENT ON COLUMN users.bank_code IS 'Bank code for VietQR (e.g., 970436 for VCB)';

SELECT 'Bank account fields migration completed!' AS status;
