<?php

require_once "includes/init.php";
require_once "includes/Model.php";

class {context.class_name} extends AbstractDBModel {{
{context.declare_properties}

  public function __construct({context.properties}) {{
{context.ctor_assignments}
  }}

  // GETTERS & SETTERS
{context.define_getters_and_setters}

  // STATIC
  // convenience find methods
{context.define_find_methods}
}}

{context.class_name}::init($db_connector, "{context.table_name}");

?>
