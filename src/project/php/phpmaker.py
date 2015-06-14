from src import projectMaker

import re
import string
import os
import inspect

from .phpmodel import PHPModel


def snake_to_camel_case(s):
    return "".join(word.capitalize() for word in s.split("_"))

def camel_to_snake_case(s):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def string_to_camel_case(s):
    pass

def string_to_snake_case(s):
    pass



class PHPMaker(projectMaker.Maker):

    def setup(self):
        super().setup()
        if "core" not in self.config:
            self.config["core"] = False
        if not self.config["core"]:
            self.path = "php"

    def core(self, config):
        yield {"index.php": self.load_template("index.php")}

    def database(self, config):
        if config["database_connector"].lower() == "pdo":
            connector_class = "PDODBConnector"
        else:
            connector_class = "MySQLiDBConnector"

        yield {"includes": {
            "init.php": self.load_template(
                "init.php",
                connector_class=connector_class,
                **self.config["database"]
            )
        }}

        for file_name in ["DBConnector.php", "MySQLiDBConnector.php", "PDODBConnector.php", "Model.php", "functions.php"]:
            yield {file_name: self.load_template(file_name, no_context=True)}


    def models(self, config):
        for model_name, model_config in config.items():
            class_name = snake_to_camel_case(model_name)
            table_name = class_name + "s"

            if "plural" in model_config:
                table_name = model_config["plural"]

            table_name = table_name.lower()

            with open(inspect.getfile(self.__class__).rpartition("/")[0] +  "/templates/model_template.php") as model_template:
                model = PHPModel(
                    model_template.read(), class_name, table_name, model_config["fields"])

                yield {"models": {class_name.lower() + ".php": model.gen_code()}}

        yield {"models": {
            "require_all.php": "<?php\n\n{}\n ?>".format("".join(
                ('require_once "{}";\n'.format(snake_to_camel_case(name)))
                for name in config
            ))
        }}

    # this is toooo long and difficult
    def routes(self, config):
        #routing_mode = config["routing"] if "routing" in config else "simple"
        routing_mode = "simple"

        yield {"index": {"api.php": self.load_template("define_routes.php")}}

        # this should probably not be here^^
        funcs = []
        for method, routes_data in config.items():
            request_var = "$_" + method.upper()

            for route, params in routes_data.items():

                check_vars = " && ".join("isset(" + request_var + "[\"" + param + "\"])" for param in params)

                api_controller_call = "$api_controller->{route}(array({params}))".format(
                    route=route,
                    params=", ".join('"{param}" => ${param}'.format(param=param)
                        for param in params
                    ),
                )

                yield {"api": {
                    "route.php": self.load_template("api_file_template.php",
                        check_vars = check_vars,
                        assign_vars = "\n    ".join(
                            '${param} = ({type}) {request_var}["{param}"];'.format(
                                param=param,
                                type=val,
                                request_var=request_var,
                            )
                            for param, val in params.items() if param != "format"),
                        format = params.get("format", "string"),
                        output = (
                            api_controller_call
                            if params.get("format", "string") == "string"
                            else "json_encode(" + api_controller_call + ")"
                        )
                    )
                }}

                funcs.append(self.load_template("func_template",
                    func_name = route,
                    assign_vars = "".join(
                        ('        ${param} = $params["{param}"];\n'.format(
                            param=param))
                        for param in params),
                    pre_output = '""' if params.get("format", "string") == "string" else "array()",
                ))

        route_method = {route:method
            for method, routes_data in config.items()
            for route in routes_data}

        yield {"controllers": {
            "ApiController.php": self.load_template("controller_template.php",
                route_types = ",\n        ".join(
                    '"{route}" => "{method}"'.format(route=route, method=method)
                    for route, method in route_method.items()),
                define_controller_functions = "".join(funcs)
            )
        }}



    def controllers(self, config):

        for controller in config:
            yield {"controllers": {
                controller + ".php": ('<?php\n'
                    'require_once "models/require_all.php";\n'
                    '?>')
            }}

        yield {"controllers": {"require_all.php": "<?php\n\n{}\n?>".format(
            "".join('require_once "' + controller + '";\n' for controller in config)
        )}}
