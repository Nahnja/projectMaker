<?php

require_once "DBConnector.php";

class MySQLiDBConnector implements DBConnector {

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

        $this->mysqli   = new mysqli($domain, $user, $pw, $name);

        $this->connected = TRUE;
    }

    public function connect() {
        if (!$this->connected) {
            $this->mysqli = new mysqli($this->domain, $this->user, $this->pw, $this->name);

            if($this->mysqli->connect_errno !== 0) {
                return FALSE;
            }
            $this->connected = TRUE;
        }
        return TRUE;
    }

    public function disconnect()	{
        if ($this->connected) {
            if($this->mysqli->close()) {
                $this->mysqli = NULL;
                $this->connected = FALSE;
                return TRUE;
            }
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
            $statement = $this->mysqli->query($query);
            $this->lastStatement = $statement;
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
        if ($this->lastStatement !== NULL && $this->lastStatement !== FALSE) {
            return $this->lastStatement->fetch_all();
        }
        return array();
    }

    public function fetch_fields() {
        if ($this->lastStatement !== NULL && $this->lastStatement !== FALSE) {
            return $this->lastStatement->fetch_fields();
        }

        return array();
    }
}



?>
