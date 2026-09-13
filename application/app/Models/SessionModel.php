<?php
// Named SessionModel (not "Session") to avoid confusion with PHP's own session.
class SessionModel
{
    public static function create($learnerId, $teacherId, $offerId, $scheduledAt)
    {
        Database::run(
            "INSERT INTO sessions (learner_id, teacher_id, offer_id, scheduled_at, status)
             VALUES (?, ?, ?, ?, 'pending')",
            [$learnerId, $teacherId, $offerId, $scheduledAt]
        );
        return Database::lastId();
    }

    public static function find($id)
    {
        return Database::row("SELECT * FROM sessions WHERE id = ?", [$id]);
    }

    public static function setStatus($id, $status)
    {
        Database::run("UPDATE sessions SET status = ? WHERE id = ?", [$status, $id]);
    }

    public static function forTeacher($teacherId)
    {
        return Database::rows(
            "SELECT se.*, o.title, learner.name AS learner_name
             FROM sessions se
             JOIN offers o      ON o.id = se.offer_id
             JOIN users learner ON learner.id = se.learner_id
             WHERE se.teacher_id = ? ORDER BY se.created_at DESC",
            [$teacherId]
        );
    }

    public static function forLearner($learnerId)
    {
        return Database::rows(
            "SELECT se.*, o.title, teacher.name AS teacher_name, r.id AS review_id
             FROM sessions se
             JOIN offers o      ON o.id = se.offer_id
             JOIN users teacher ON teacher.id = se.teacher_id
             LEFT JOIN reviews r ON r.session_id = se.id
             WHERE se.learner_id = ? ORDER BY se.created_at DESC",
            [$learnerId]
        );
    }
}
