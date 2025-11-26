-- Add is_admin column to user table
ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;

-- Create an admin user for testing (password is 'admin123')
UPDATE user SET is_admin = TRUE WHERE email = 'admin@theatre.com';
