<?php
class Skill
{
    public static function all()
    {
        return Database::rows("SELECT * FROM skills ORDER BY category, name");
    }

    public static function create($name, $category)
    {
        Database::run("INSERT INTO skills (name, category) VALUES (?, ?)", [$name, $category]);
        return Database::lastId();
    }

    public static function delete($id)
    {
        Database::run("DELETE FROM skills WHERE id = ?", [$id]);
    }

    public static function count()
    {
        return (int) Database::scalar("SELECT COUNT(*) FROM skills");
    }
}
