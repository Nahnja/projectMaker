<?php

interface Model {
    // STATIC
    // public static function from_db($data);
    public static function init($db_connector, $table_name);

    // getters, setters
    public static function set_db_connector($db_connector);
    public static function get_db_connector();
    public static function get_columns();

    // get all records from the db. if $create_objects is TRUE record instances will be returned - otherwise an array
    public static function all($create_objects);
    // get the number of records that are saved in the db
    public static function count();
    // creates a record instance and saves it to the db
    public static function create($data);
    // short cut for finding and deleting
    public static function delete($id);
    // short cut for finding and deleting
    public static function delete_by($param);
    // finds a record instance by id
    public static function find($id);
    // finds a record instance by any record attribute (given as associative array or string)
    public static function find_by($param);
    // finds a record instance by any record attribute (given as string) - subset of find_by's functionality
    public static function where($condition);



    // NON-STATIC

    // get the record instance data as associative array: [col1 => val1, col2 => val2, ...]
    public function get_attributes();
    public function get_class_name();
    // deletes the record from db if saved (naming due to PHP being unable to have same name for static and non-static functions)
    public function remove();
    // indicates whether the record instance is saved in the DB (in some state...not necessarily the current instance's state)
    // public function is_persistent($param);
    public function is_persistent();
    // saves or updates the record instance to the db
    public function save();
}


// IMPLICIT CONFIGURATIONS:
// 1. The id column is always called "id".
// (2. The id column is the first column.)
// 3. id does AUTO_INCREMENT
// 4. id === NULL <=> instance is not saved in db

abstract class AbstractDBModel implements Model {

    // STATIC PROPERTIES
    // string
    protected static $_class_name   = "";
    // string
    protected static $_table_name   = "";
    // array
    protected static $_column_names = array();
    // DBConnector
    protected static $_db_connector = NULL;
    // boolean
    protected static $_initialized  = FALSE;

    // INSTANCE PROPERTIES
    // integer
    protected $id;


    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // CONSTRUCTOR
    public function __construct($data=NULL) {
        if (!static::$_initialized) {
            throw new Exception("Class () must be initialized (with at least a DBConnector) first!", 1);
        }

        if ($data !== NULL) {
            foreach ($data as $key => $value) {
                if (is_numeric($key)) {
                    $key = static::$_column_names[$key];
                }

                // set all properties but id
                if ($key != "id") {
                    $this->$key = $value;
                }
                // id => make sure it's a number
                else {
                    $this->id = (integer) $value;
                }
            }
        }
        else {
            $this->id = NULL;
        }
    }


    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // STATIC METHODS

    // AbstractDBModel::create() is defined below under the section "ACTIVE-RECORD CLASS METHODS"

    public static function init($db_connector=NULL, $table_name=NULL) {
        static::$_db_connector = $db_connector;

        if ($table_name === NULL) {
            static::$_table_name = strtolower(get_called_class())."s";
        }
        else {
            static::$_table_name = $table_name;
        }

        $field_data = static::$_db_connector->force_query("SELECT * FROM ".static::$_table_name." LIMIT 1;")->fetch_fields();

        for ($i = 0; $i < count($field_data); $i++) {
            $field_datum = $field_data[$i];
            if (isset($field_datum->name)) {
                array_push(static::$_column_names, $field_datum->name);
            }
            else {
                array_push(static::$_column_names, $field_datum["name"]);
            }
        }

        static::$_class_name    = get_called_class();
        static::$_initialized   = TRUE;
    }

    // TODO: how to return current class? -> override or no chaining
    public static function set_db_connector($db_connector) {
        static::$_db_connector = $db_connector;
    }

    public static function get_db_connector() {
        return static::$_db_connector;
    }

    public static function get_columns() {
        return static::$_column_names;
    }

    private static function objects_from_all_fetched($fetched) {
        $result = array();
        for ($i = 0; $i < count($fetched); $i++) {
            array_push($result, new static($fetched[$i]));
        }
        return $result;
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // ACTIVE-RECORD CLASS METHODS
    public static function all($create_objects=FALSE) {
        $records = static::$_db_connector->force_query("SELECT * FROM ".(static::$_table_name).";");
        $fetched = $records->fetch_all();
        if (!$create_objects) {
            return $fetched;
        }
        // else: create instances from table data
        return static::objects_from_all_fetched($fetched);
    }

    public static function count() {
        $count = static::$_db_connector->force_query("SELECT count(*) FROM ".static::$_table_name.";")->fetch_all();
        return $count[0][0];
    }

    public static function create($data=NULL) {
        $instance = new static($data);
        $instance->save();
        return $instance;
    }

    // short cut for finding and deleting
    public static function delete($id) {
        return static::$_db_connector->force_query("DELETE FROM ".static::$_table_name." WHERE id=".$id.";") !== FALSE;
    }

    // short cut for finding and deleting
    public static function delete_by($param) {
        if (!is_string($param)) {
            $condition = "";
            foreach (static::get_columns() as $idx => $col) {
                $val = NULL;
                // check assoc array
                if (isset($param[$col])) {
                    $val = $param[$col];
                }
                // check object
                elseif (isset($param->$col)) {
                    $val = $param->$col;
                }

                if ($val !== NULL) {
                    if (!is_numeric($val)) {
                        $val = "'".$val."'";
                    }
                    $condition .= $col."=".$val." AND ";
                }
            }
            $condition = rtrim($condition, " AND ");
        }
        else {
            $condition = $param;
        }

        return static::$_db_connector->force_query("DELETE FROM ".static::$_table_name." WHERE ".$condition.";") !== FALSE;
    }

    public static function find($id) {
        $records = static::$_db_connector->force_query("SELECT * FROM ".(static::$_table_name)." WHERE id=".$id.";");

        if ($records) {
            $fetched = $records->fetch_all();

            if (count($fetched) === 1) {
                return new static($fetched[0]);
            }
        }

        return NULL;
    }

    public static function find_by($param) {
        if (!is_string($param)) {
            $condition = "";
            foreach (static::get_columns() as $idx => $col) {
                $val = NULL;
                // check assoc array
                if (isset($param[$col])) {
                    $val = $param[$col];
                }
                // check object
                elseif (isset($param->$col)) {
                    $val = $param->$col;
                }

                if ($val !== NULL) {
                    if (!is_numeric($val)) {
                        $val = "'".$val."'";
                    }
                    $condition .= $col."=".$val." AND ";
                }
            }
            $condition = rtrim($condition, " AND ");
        }
        else {
            $condition = $param;
        }{

        $records = static::$_db_connector->force_query("SELECT * FROM ".static::$_table_name." WHERE ".$condition.";");

        if ($records) {
            return static::objects_from_all_fetched($records->fetch_all());
        }

        return array();
    }

    /**
 	 * @param condition {string}
	 */
    public static function where($condition) {
        return static::$_db_connector->force_query("SELECT * FROM ".(static::$name)." WHERE ".$condition.";")->fetch_all();
    }


    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // INSTANCE METHODS

    public function remove() {
        return static::delete($this->id);
    }

    public function get_attributes() {
        $result = array();
        foreach (static::$_column_names as $idx => $name) {
            $result[$name] = $this->$name;
        }
        return $result;
    }

    // GETTERS & SETTERS

    public function get_class_name() {
        return get_class($this);
    }

    public function is_persistent() {
        return $this->id !== NULL;
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // ACTIVE-RECORD INSTANCE METHODS
    /**
     * save record to database leaving the connector unchanged
     */
    public function save() {
        // no in DB => insert
        if (!$this->is_persistent()) {

            $values = array();
            foreach (static::$_column_names as $idx => $name) {
                $value = $this->$name;
                if ($value === NULL) {
                    $value = "NULL";
                }
                elseif(!is_numeric($value)) {
                    $value = "'".addslashes($value)."'";
                }
                array_push($values, $value);
            }

            static::$_db_connector->force_query(
                "INSERT INTO ".(static::$_table_name)." VALUES (".implode(",", $values).");"
            );
        }
        // already in DB => update
        else {
            static::$_db_connector->force_query("UPDATE ".(static::$_table_name)." SET () WHERE id=".$this->id.";");
        }

        return $this;
    }
}

?>
