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

        if "core" not in self.config or not self.config["core"]:
            self.path += "/php"
            del self.config["core"]
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        with open(self.path + "/index.php", "w") as index_php:
            index_php.write(self.load_template("index.php"))


    def database(self, config):
        if config["database_connector"].lower() == "mysqli":
            connector_class = "MySQLiDBConnector"
        elif config["database_connector"].lower() == "pdo":
            connector_class = "PDODBConnector"
        else:
            connector_class = "MySQLiDBConnector"


        if not os.path.exists(self.path + "/includes"):
            os.makedirs(self.path + "/includes")

        with open(self.path + "/includes/init.php", "w") as init_php:
            init_php.write(
                self.load_template(
                    "init.php",
                    connector_class=connector_class,
                    **self.config["database"]
                )
            )

        for file_name in ["DBConnector.php", "MySQLiDBConnector.php", "PDODBConnector.php", "Model.php", "functions.php"]:
            with open(self.path + "/" + file_name, "w") as out:
                out.write(self.load_template(file_name, no_context=True))


    def models(self, config):

        if not os.path.exists(self.path + "/models"):
            os.makedirs(self.path + "/models")

        file_names = []
        for model_name, model_config in config.items():
            class_name = snake_to_camel_case(model_name)
            table_name = class_name + "s"

            if "plural" in model_config:
                table_name = model_config["plural"]

            table_name = table_name.lower()

            with open(inspect.getfile(self.__class__).rpartition("/")[0] +  "/templates/model_template.php") as model_template:
                model = PHPModel(
                    model_template.read(), class_name, table_name, model_config["fields"])

                with open(self.path + "/models/" + class_name.lower() + ".php", "w") as out:
                    out.write(model.gen_code())
                    file_names.append(class_name.lower())


        with open(self.path + "/models/require_all.php", "w") as require_all:
            require_all.write(
                "<?php\n\n{}\n ?>".format("".join(
                        ('require_once "{}";\n'.format(name))
                        for name in file_names
                    )
                )
            )

    def routes(self, config):
        #routing_mode = config["routing"] if "routing" in config else "simple"
        routing_mode = "simple"

        if not os.path.exists(self.path + "/index"):
            os.makedirs(self.path + "/index")
        if not os.path.exists(self.path + "/controllers"):
            os.makedirs(self.path + "/controllers")

        with open(self.path + "/index/api.php", "w") as api_php:
            api_php.write(self.load_template("define_routes.php"))

        with open(self.path + "/controllers/ApiController.php", "w") as api_controller_php:
            funcs = []

            for method, routes_data in config.items():
                for route, params in routes_data.items():

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

            api_controller_php.write(self.load_template("controller_template.php",
                route_types = ",\n        ".join(
                    '"{route}" => "{method}"'.format(route=route, method=method)
                    for route, method in route_method.items()),
                define_controller_functions = "".join(funcs)
            ))


        #result["api"] = make_api_files(routes_config)

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

                if not os.path.exists(self.path + "/api"):
                    os.makedirs(self.path + "/api")

                with open(self.path + "/api/" + route + ".php", "w") as route_php:
                    route_php.write(self.load_template("api_file_template.php",
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
                    ))




    def controllers(self, config):

        if not os.path.exists(self.path + "/controllers"):
            os.makedirs(self.path + "/controllers")

        for controller in config:
            with open(self.path + "/controllers/" + controller + ".php", "w") as controller_php:
                controller_php.write("""<?php
                require_once "models/require_all.php";
                ?>""")

        with open(self.path + "/controllers/require_all.php", "w") as out:
            out.write("<?php\n\n{}\n ?>".format(
                "".join('require_once "' + controller + '";\n' for controller in config)
            ))
