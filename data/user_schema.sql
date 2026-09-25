-- MindTrack: Users table (accounts created via Sign Up)
-- The app saves rows through Python (register\_user), NOT by inserting here directly,
-- because passwords must be hashed (PBKDF2-SHA256, 200k iterations) before storage.

CREATE TABLE IF NOT EXISTS users (
    email         TEXT PRIMARY KEY,          -- normalized to lowercase in the app
    name          TEXT NOT NULL,             -- display name
    password\_hash TEXT NOT NULL,             -- never store plain passwords!
    salt          TEXT NOT NULL,             -- random per-user salt (hex, 32 chars)
    created\_at    TEXT NOT NULL              -- 'YYYY-MM-DD HH:MM:SS'
);

-- Example row shape (hash/salt below are NOT real — the app generates them at signup):
-- INSERT INTO users (email, name, password\_hash, salt, created\_at)
-- VALUES ('alex@example.com', 'Alex Kumar', 'ab12cd...', '9f3e...', '2026-09-24 21:24:00');

-- ── Useful queries ──
-- All accounts, newest first:
-- SELECT email, name, created\_at FROM users ORDER BY created\_at DESC;

-- Change password for one account (then let them re-sign-in):
-- (do this via the app so the hash/salt are regenerated correctly)

-- Delete an account:
-- DELETE FROM users WHERE email = 'alex@example.com'; 
