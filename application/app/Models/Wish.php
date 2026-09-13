<?php
class Wish
{
    public static function forUser($userId)
    {
        return Database::rows(
            "SELECT w.id, s.name AS skill, s.category
             FROM wishes w JOIN skills s ON s.id = w.skill_id
             WHERE w.user_id = ? ORDER BY s.category, s.name",
            [$userId]
        );
    }

    public static function add($userId, $skillId)
    {
        // INSERT IGNORE relies on the UNIQUE(user_id, skill_id) key to skip duplicates.
        Database::run("INSERT IGNORE INTO wishes (user_id, skill_id) VALUES (?, ?)", [$userId, $skillId]);
    }

    public static function remove($wishId, $userId)
    {
        Database::run("DELETE FROM wishes WHERE id = ? AND user_id = ?", [$wishId, $userId]);
    }

    // The two-way swap query: someone who teaches a skill I want, while I teach a
    // skill they want.
    public static function mutualMatches($userId)
    {
        return Database::rows(
            "SELECT DISTINCT other.id, other.name,
                    theirSkill.name AS they_teach,
                    mySkill.name    AS i_teach
             FROM users other
             JOIN offers o1        ON o1.user_id = other.id AND o1.status = 'active'
             JOIN wishes myWish    ON myWish.user_id = ? AND myWish.skill_id = o1.skill_id
             JOIN skills theirSkill ON theirSkill.id = o1.skill_id
             JOIN offers o2        ON o2.user_id = ? AND o2.status = 'active'
             JOIN wishes theirWish ON theirWish.user_id = other.id AND theirWish.skill_id = o2.skill_id
             JOIN skills mySkill   ON mySkill.id = o2.skill_id
             WHERE other.id <> ?",
            [$userId, $userId, $userId]
        );
    }
}
