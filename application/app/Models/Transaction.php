<?php
class Transaction
{
    public static function record($fromUser, $toUser, $sessionId, $credits = 1)
    {
        Database::run(
            "INSERT INTO transactions (from_user, to_user, session_id, credits)
             VALUES (?, ?, ?, ?)",
            [$fromUser, $toUser, $sessionId, $credits]
        );
    }
}
