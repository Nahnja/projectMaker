<?php

// require_once "../models/require_all.php";

class ApiController {{

  private $route_types = array(
      {route_types}
  );

  public function __construct() {{

  }}

  public function route_is_valid($route, $type) {{
      return isset($this->route_types[$type]);
  }}

{define_controller_functions}

}}

?>
