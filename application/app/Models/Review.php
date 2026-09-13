<?php
class Review
{
    public static function forSession($sessionId)
    {
        return Database::row("SELECT * FROM reviews WHERE session_id = ?", [$sessionId]);
    }

    public static function create($sessionId, $reviewerId, $rating, $comment)
    {
        Database::run(
            "INSERT INTO reviews (session_id, reviewer_id, rating, comment) VALUES (?, ?, ?, ?)",
            [$sessionId, $reviewerId, $rating, $comment]
        );
    }

    // Average rating + count for one offer (across its completed sessions).
    public static function summaryForOffer($offerId)
    {
        return Database::row(
            "SELECT AVG(r.rating) AS avg_rating, COUNT(*) AS cnt
             FROM reviews r JOIN sessions se ON se.id = r.session_id
             WHERE se.offer_id = ?",
            [$offerId]
        );
    }

    public static function listForOffer($offerId)
    {
        return Database::rows(
            "SELECT r.rating, r.comment, u.name AS reviewer
             FROM reviews r
             JOIN sessions se ON se.id = r.session_id
             JOIN users u     ON u.id = r.reviewer_id
             WHERE se.offer_id = ?
             ORDER BY r.created_at DESC LIMIT 10",
            [$offerId]
        );
    }
}
