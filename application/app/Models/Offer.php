<?php
class Offer
{
    // Columns we repeatedly need joined to the teacher + skill.
    private const SELECT =
        "SELECT o.id, o.title, o.description, o.level, o.status, o.user_id, o.skill_id,
                u.name AS teacher, u.id AS teacher_id, s.name AS skill, s.category
         FROM offers o
         JOIN users  u ON u.id = o.user_id
         JOIN skills s ON s.id = o.skill_id";

    public static function active()
    {
        return Database::rows(self::SELECT . " WHERE o.status = 'active' ORDER BY o.created_at DESC");
    }

    public static function search($q)
    {
        $like = '%' . $q . '%';
        return Database::rows(
            self::SELECT . " WHERE o.status = 'active'
                AND (s.name LIKE ? OR o.title LIKE ? OR s.category LIKE ?)
             ORDER BY o.created_at DESC",
            [$like, $like, $like]
        );
    }

    public static function find($id)
    {
        return Database::row(self::SELECT . " WHERE o.id = ?", [$id]);
    }

    public static function forUser($userId)
    {
        return Database::rows(
            "SELECT o.*, s.name AS skill
             FROM offers o JOIN skills s ON s.id = o.skill_id
             WHERE o.user_id = ? ORDER BY o.created_at DESC",
            [$userId]
        );
    }

    // Returns the owned offer or null (used to confirm ownership before edit).
    public static function findOwned($id, $userId)
    {
        return Database::row("SELECT * FROM offers WHERE id = ? AND user_id = ?", [$id, $userId]);
    }

    public static function create($userId, $skillId, $title, $description, $level)
    {
        Database::run(
            "INSERT INTO offers (user_id, skill_id, title, description, level)
             VALUES (?, ?, ?, ?, ?)",
            [$userId, $skillId, $title, $description, $level]
        );
        return Database::lastId();
    }

    public static function update($id, $userId, $skillId, $title, $description, $level, $status)
    {
        Database::run(
            "UPDATE offers SET skill_id = ?, title = ?, description = ?, level = ?, status = ?
             WHERE id = ? AND user_id = ?",
            [$skillId, $title, $description, $level, $status, $id, $userId]
        );
    }

    public static function delete($id, $userId)
    {
        Database::run("DELETE FROM offers WHERE id = ? AND user_id = ?", [$id, $userId]);
    }

    public static function count()
    {
        return (int) Database::scalar("SELECT COUNT(*) FROM offers");
    }
}
