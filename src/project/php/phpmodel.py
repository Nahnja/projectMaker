class PHPModel():

    def __init__(self, template, class_name, table_name, fields):
        self.template = template
        self.class_name = class_name
        self.table_name = table_name
        self.fields = fields

    def gen_code(self):
        return self.template.format(context = self)

    @property
    def properties(self):
        return ", ".join("$" + field["name"] for field in self.fields)

    @property
    def declare_properties(self, indentation=4):
        indentation = " " * indentation

        template = (
            indentation + "// {type}\n" +
            indentation + "{visibility} ${var_name};\n"
        )

        return "".join(
            template.format(
                type = field.get("type", "..."),
                visibility = field.get("visibility", "protected"),
                var_name = field["name"]
            )
            for field in self.fields
        )

    @property
    def define_getters_and_setters(self, indentation=4):
        indentation = " " * indentation

        template = (
            indentation + "public function {setter_name}(${var_name}) {{\n" +
            indentation + "    $this->{var_name} = ${var_name};\n" +
            indentation + "    return $this;\n" +
            indentation + "}}\n\n" +
            indentation + "public function {getter_name}() {{\n" +
            indentation + "    return $this->${var_name};\n" +
            indentation + "}}\n\n"
        )

        return "".join(
            template.format(
                setter_name = "set_" + field["name"],
                getter_name = "get_" + field["name"],
                var_name    = field["name"],
            )
            for field in self.fields
        )

    @property
    def define_find_methods(self, indentation=4):
        indentation = " " * indentation

        template = (
            indentation + "public static function find_by_{var_name}(${var_name}) {{\n" +
            indentation + "    return static::find_by(array(\"{var_name}\" => ${var_name}));\n" +
            indentation + "}}\n\n"
        )

        return "".join(
            template.format(
                var_name    = field["name"],
            )
            for field in self.fields
        )

    @property
    def ctor_assignments(self, indentation=4):
        indentation = " " * indentation
        return "\n".join(
            (indentation + "$this->" + field["name"] + " = $" + field["name"] + ";")
            for field in self.fields)
