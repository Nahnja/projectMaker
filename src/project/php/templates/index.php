<?php
  // session_start();
  require_once "includes/functions.php";

  $page = "home";

  if (isset($_REQUEST['page'])) {{
      $page = $_REQUEST['page'];
      if (!logged_in() && !in_array($page, array("home", "kontakt", "impressum"))) {{
          $page = "home";
      }}
  }}

  ?>
  <!DOCTYPE html>
  <html>
      <?php
          require_once "views/head.php";
      ?>
      <body>
          <div id="page">
              <div id="header"></div>

              <div id="content">
                  <?php
                      if (file_exists("views/$page.php")) {{
                          require_once "views/$page.php";
                      }}
                      else {{
                          require_once "views/home.php";
                      }}
                  ?>
              </div>

              <div id="footer"></div>
          </div>
      </body>
  </html>
