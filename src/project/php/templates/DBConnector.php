<?php

interface DBConnector {
    public function connect();
    public function disconnect();

    public function is_connected();

    public function query($query);
    public function force_query($query);

    // NOTE: this may need to be extended because the non-standard API of the native connectors has to be caught here
    public function fetch_all();
    public function fetch_fields();
}

?>
