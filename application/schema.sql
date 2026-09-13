-- ============================================================
-- SkillBank database schema + starter data
-- How to use: open phpMyAdmin (http://localhost/phpmyadmin) ->
--   Import -> choose this file -> Go.  (Or run it from the SQL tab.)
-- This drops and recreates the database, so it is safe to re-run.
-- After this, run seed.php once in the browser to create demo accounts.
-- ============================================================

DROP DATABASE IF EXISTS skillbank;
CREATE DATABASE skillbank CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE skillbank;

-- People. credits = the time-currency. New members start with 3.
CREATE TABLE users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  email         VARCHAR(150) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role          ENUM('admin','member') NOT NULL DEFAULT 'member',
  credits       INT NOT NULL DEFAULT 3,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- The catalog of teachable skills (managed by the admin).
CREATE TABLE skills (
  id       INT AUTO_INCREMENT PRIMARY KEY,
  name     VARCHAR(100) NOT NULL,
  category VARCHAR(80)  NOT NULL DEFAULT 'General'
);

-- A member's listing: "I can teach X". This is the main CRUD entity.
CREATE TABLE offers (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  skill_id    INT NOT NULL,
  title       VARCHAR(150) NOT NULL,
  description TEXT,
  level       ENUM('Beginner','Intermediate','Advanced') NOT NULL DEFAULT 'Beginner',
  status      ENUM('active','inactive') NOT NULL DEFAULT 'active',
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- A booking: learner asks to learn from teacher. Moves through a status workflow:
-- pending -> accepted -> completed   (or cancelled at any point before completion).
CREATE TABLE sessions (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  learner_id   INT NOT NULL,
  teacher_id   INT NOT NULL,
  offer_id     INT NOT NULL,
  scheduled_at DATETIME NULL,
  status       ENUM('pending','accepted','completed','cancelled') NOT NULL DEFAULT 'pending',
  created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (learner_id) REFERENCES users(id)  ON DELETE CASCADE,
  FOREIGN KEY (teacher_id) REFERENCES users(id)  ON DELETE CASCADE,
  FOREIGN KEY (offer_id)   REFERENCES offers(id) ON DELETE CASCADE
);

-- The ledger. One row per completed session = proof a credit moved.
-- This table is what makes SkillBank an "economy" instead of a plain board.
CREATE TABLE transactions (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  from_user  INT NOT NULL,
  to_user    INT NOT NULL,
  session_id INT NOT NULL,
  credits    INT NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (from_user)  REFERENCES users(id),
  FOREIGN KEY (to_user)    REFERENCES users(id),
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

-- A learner's 1-5 star review of a completed session. One review per session.
CREATE TABLE reviews (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  session_id  INT NOT NULL UNIQUE,
  reviewer_id INT NOT NULL,
  rating      TINYINT NOT NULL,
  comment     TEXT,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id)  REFERENCES sessions(id) ON DELETE CASCADE,
  FOREIGN KEY (reviewer_id) REFERENCES users(id)    ON DELETE CASCADE
);

-- Skills a member WANTS to learn. Powers the "mutual match" suggestions.
CREATE TABLE wishes (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  skill_id   INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uniq_wish (user_id, skill_id),
  FOREIGN KEY (user_id)  REFERENCES users(id)  ON DELETE CASCADE,
  FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- Starter skill catalog so the app isn't empty on first run.
INSERT INTO skills (name, category) VALUES
('Python Programming', 'Programming'),
('Web Development',     'Programming'),
('Guitar',             'Music'),
('Public Speaking',    'Soft Skills'),
('Graphic Design',     'Design'),
('Calculus',           'Academics');
