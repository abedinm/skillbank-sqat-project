<?php
class User
{
    public static function find($id)
    {
        return Database::row("SELECT * FROM users WHERE id = ?", [$id]);
    }

    public static function findByEmail($email)
    {
        return Database::row("SELECT * FROM users WHERE email = ?", [$email]);
    }

    public static function emailExists($email)
    {
        return Database::scalar("SELECT COUNT(*) FROM users WHERE email = ?", [$email]) > 0;
    }

    public static function create($name, $email, $passwordHash)
    {
        Database::run(
            "INSERT INTO users (name, email, password_hash, role, credits)
             VALUES (?, ?, ?, 'member', 3)",
            [$name, $email, $passwordHash]
        );
        return Database::lastId();
    }

    public static function changeCredits($id, $delta)
    {
        Database::run("UPDATE users SET credits = credits + ? WHERE id = ?", [$delta, $id]);
    }

    public static function credits($id)
    {
        return (int) Database::scalar("SELECT credits FROM users WHERE id = ?", [$id]);
    }

    public static function all()
    {
        return Database::rows("SELECT id, name, email, role, credits FROM users ORDER BY id");
    }

    public static function count()
    {
        return (int) Database::scalar("SELECT COUNT(*) FROM users");
    }
}
