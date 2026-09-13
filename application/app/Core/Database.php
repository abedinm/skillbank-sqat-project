<?php
// Thin wrapper around mysqli so models never repeat connect/prepare/execute.
// One shared connection per request. Uses PHP 8.1+ execute($params) so we get
// prepared-statement safety (no SQL injection) without manual bind_param.
class Database
{
    private static $conn = null;

    public static function conn()
    {
        if (self::$conn === null) {
            $host = getenv('SB_DB_HOST') ?: 'localhost';
            $user = getenv('SB_DB_USER') ?: 'root';
            $pass = getenv('SB_DB_PASS') !== false ? getenv('SB_DB_PASS') : '';
            $name = getenv('SB_DB_NAME') ?: 'skillbank';
            $port = (int)(getenv('SB_DB_PORT') ?: 3306);
            self::$conn = mysqli_connect($host, $user, $pass, $name, $port);
            if (!self::$conn) {
                die('Database connection failed: ' . mysqli_connect_error());
            }
            mysqli_set_charset(self::$conn, 'utf8mb4');
        }
        return self::$conn;
    }

    // Prepare + execute with bound params. Returns the statement.
    public static function run($sql, $params = [])
    {
        $stmt = mysqli_prepare(self::conn(), $sql);
        mysqli_stmt_execute($stmt, $params ?: null);
        return $stmt;
    }

    // Fetch many rows as associative arrays.
    public static function rows($sql, $params = [])
    {
        $res = mysqli_stmt_get_result(self::run($sql, $params));
        return $res ? mysqli_fetch_all($res, MYSQLI_ASSOC) : [];
    }

    // Fetch a single row (or null).
    public static function row($sql, $params = [])
    {
        $res = mysqli_stmt_get_result(self::run($sql, $params));
        return $res ? (mysqli_fetch_assoc($res) ?: null) : null;
    }

    // Single scalar value (e.g. a COUNT).
    public static function scalar($sql, $params = [])
    {
        $res = mysqli_stmt_get_result(self::run($sql, $params));
        $row = $res ? mysqli_fetch_row($res) : null;
        return $row ? $row[0] : null;
    }

    public static function lastId()
    {
        return mysqli_insert_id(self::conn());
    }
}
