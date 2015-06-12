<?php

// called from api.php (included from there) => go from api.php's path
if (file_exists("controllers/ApiController.php")) {{
  require_once "controllers/ApiController.php";
}}
// called from here => go from here
else {{
  require_once "../controllers/ApiController.php";
}}

$api_controller = new ApiController();

if ({check_vars}) {{
  {assign_vars}

  // output format: {format}
  echo {output};
}}

?>
