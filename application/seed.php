<?php
// =====================================================================
// ONE-TIME demo data. Run once from the browser, then DELETE this file.
//   built-in server:  http://localhost:8002/seed.php
//   XAMPP:            http://localhost/skillbank/seed.php
// All demo passwords are:  password123
// =====================================================================
require __DIR__ . '/app/Core/Database.php';

// Demo accounts: [name, email, role, credits]
$users = [
    ['Admin',  'admin@skillbank.test',  'admin',  99],
    ['Ayesha', 'ayesha@skillbank.test', 'member',  3],
    ['Rahim',  'rahim@skillbank.test',  'member',  3],
];
foreach ($users as [$name, $email, $role, $credits]) {
    $hash = password_hash('password123', PASSWORD_DEFAULT);
    // INSERT IGNORE so re-running doesn't error on the duplicate email.
    Database::run(
        "INSERT IGNORE INTO users (name, email, password_hash, role, credits)
         VALUES (?, ?, ?, ?, ?)",
        [$name, $email, $hash, $role, $credits]
    );
}

// Demo offers (Ayesha teaches Python, Rahim teaches Guitar).
Database::run(
    "INSERT INTO offers (user_id, skill_id, title, description, level)
     SELECT u.id, s.id, 'Learn Python basics',
            'Variables, loops and functions, explained simply.', 'Beginner'
     FROM users u, skills s
     WHERE u.email = 'ayesha@skillbank.test' AND s.name = 'Python Programming' LIMIT 1"
);
Database::run(
    "INSERT INTO offers (user_id, skill_id, title, description, level)
     SELECT u.id, s.id, 'Acoustic guitar for starters',
            'Your first chords and a full song.', 'Beginner'
     FROM users u, skills s
     WHERE u.email = 'rahim@skillbank.test' AND s.name = 'Guitar' LIMIT 1"
);

// Wishlists that create a mutual match (Ayesha wants Guitar, Rahim wants Python).
Database::run(
    "INSERT IGNORE INTO wishes (user_id, skill_id)
     SELECT u.id, s.id FROM users u, skills s
     WHERE u.email = 'ayesha@skillbank.test' AND s.name = 'Guitar'"
);
Database::run(
    "INSERT IGNORE INTO wishes (user_id, skill_id)
     SELECT u.id, s.id FROM users u, skills s
     WHERE u.email = 'rahim@skillbank.test' AND s.name = 'Python Programming'"
);

echo 'Seed complete. Login as admin@skillbank.test / password123. Now DELETE seed.php.';
