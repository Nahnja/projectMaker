<?php

function delegate_route($route) {{
  if (isset($_GET[$route])) {{
      $req_type = "get";
  }}
  elseif (isset($_POST[$route])) {{
      $req_type = "post";
  }}
  else {{
      echo "{{\"error\": \"Call to undefined route!\", \"route\": \"".$route."\"}}";
      exit(0);
  }}

  require_once "api/".$route.".php";

  if ($api_controller->check_route($route, $req_type)) {{
      $api_controller->$route($_GET);
      exit(0);
  }}
}}

?>
