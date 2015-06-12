<?php

require_once "DBConnector.php";

class PDODBConnector implements DBConnector {

    // string
    private $domain;
    private $user;
    private $pw;
    private $name;

    // mysqli
    private $mysqli;

    // boolean
    private $connected;

    ////////////////////////////////////////////////////////////////////////////////////////////////////
    // CONSTRUCTOR
    public function __construct($domain, $user, $pw, $name) {
        $this->domain   = $domain;
        $this->user     = $user;
        $this->pw       = $pw;
        $this->name     = $name;
        $this->lastStatement = NULL;

        $this->pdo      = new PDO(
            "mysql:host=".$domain.";dbname=".$name,
            $user,
            $pw,
            array(PDO::ATTR_ERRMODE=> PDO::ERRMODE_EXCEPTION,PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8")
        );

        $this->connected = TRUE;
    }

    public function connect() {
        if (!$this->connected) {
            $this->pdo = new PDO(
                "mysql:host=".$domain.";dbname=".$name,
                $user,
                $pw,
                array(PDO::ATTR_ERRMODE=> PDO::ERRMODE_EXCEPTION,PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8")
            );

            if($this->pdo->connect_errno != 0) {
                return FALSE;
            }
            $this->connected = TRUE;
        }
        return TRUE;
    }

    public function disconnect()	{
        if ($this->connected) {
            $this->pdo = NULL;
            $this->connected = FALSE;
            return TRUE;
        }
        return FALSE;
    }

    public function is_connected() {
        return $this->connected === TRUE;
    }

    /**
     * Tries to execute a query. If not connected returns FALSE.
     */
    public function query($query) {
        if ($this->connected) {
            $statement = $this->pdo->prepare($query);
            $this->lastStatement = $statement;
            $statement->execute();
            return $this;
        }
        return FALSE;
    }

    /**
     * Executes a query and makes sure the connection is established at the time of querying.
     */
    public function force_query($query) {
        // connected => stay connected
        if ($this->connected) {
            return $this->query($query);
        }

        // else: not connected => connect and disconnect
        $this->connect();
        $res = $this->query($query);
        $this->disconnect();
        return $res;
    }

    public function fetch_all() {
        return $this->lastStatement->fetchAll();
    }

    // TODO: this is not very good ^^
    // right now the word after "from" is returned
    private static function get_table_name_from_query($query) {
        $parts = explode(" ", $query);
        for ($i = 0; $i < count($parts); $i++) {
            if (trim(strtolower($parts[$i])) === "from") {
                return $parts[$i + 1];
            }
        }
        return "";
    }

    public function fetch_fields() {
        $statement = $this->pdo->prepare(
            "SHOW FULL COLUMNS from ".static::get_table_name_from_query($this->lastStatement->queryString).";"
        );
        $statement->execute();
        $fetched = $statement->fetchAll();

        $result = array();
        foreach ($fetched as $idx => $data) {
            array_push($result, array("name" => $data["Field"]));
        }

        return $result;
    }
}



?>
