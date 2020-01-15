import re
import sys

class CompilationEngine:

    COMMON_PATTERNS = {
        "identifier": "^[a-zA-Z_][a-zA-Z0-9_]*",
        "type": "(int|char|boolean|^[a-zA-Z_][a-zA-Z0-9_]*)"
    }

    def __init__(self, tokenizer, symbol_table, vmwriter):
        self.class_name = ""
        self.label_num = 0

        self.tokenizer = tokenizer
        self.table = symbol_table
        self.writer = vmwriter

        # Begin the compilation
        self.tokenizer.advance()
        self.compile_class()


    def compile_class(self):
        """Compiles a complete class."""

        self.eat("class")
        self.class_name = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])
        self.eat("\{")
        # There can be zero or more class variable declarations.
        while True:
            try:
                self.compile_class_var_dec()
            except SyntaxError:
                break

        # There can be zero or more subroutines.
        while True:
            try:
                self.compile_subroutine_dec()
            except SyntaxError:
                break

        self.eat("\}")


    def compile_class_var_dec(self):
        """Compiles a static variable declaration, or a field declaration."""

        # If there are no class variable declarations, return.
        if not re.match("(static|field)", self.tokenizer.current_token):
            raise SyntaxError

        variable = {}

        self.f.write("<classVarDec>\n")

        variable["kind"] = self.eat("(static|field)")
        variable["type"] = self.eat(CompilationEngine.COMMON_PATTERNS["type"])
        variable["name"] = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])

        # Check if variable already exists in the symbol table.
        if self.var_already_defined(variable["name"]):
            print(f"Variable {variable['name']} has already been defined.")
            sys.exit(1)

        # Add the variable to the class table
        self.table.define(variable["name"], variable["type"], variable["kind"])

        self.f.write(f"<type: {variable['type']}, kind: {variable['kind']}, index: {self.table.index_of(variable['name'])}>{variable['name']}</>\n")

        # There can be zero or more additional varNames.
        while True:
            try: # This one is optional. If there is no ',' then stop searching for additional varNames.
                self.eat("\,")
            except SyntaxError:
                break

            try: # This one is mandatory. ',' must be followed by varName.
                variable["name"] = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])
            except SyntaxError:
                print("Incorrect syntax.")
                sys.exit(1)

            # Check if variable already exists in the symbol table.
            if self.var_already_defined(variable["name"]):
                print(f"Variable {variable['name']} has already been defined.")
                sys.exit(1)

            # Add the variable to the class table
            self.table.define(variable["name"], variable["type"], variable["kind"])

            self.f.write(f"<type: {variable['type']}, kind: {variable['kind']}, index: {self.table.index_of(variable['name'])}>{variable['name']}</>\n")


        self.eat("\;")

        self.f.write("</classVarDec>\n")


    def compile_subroutine_dec(self):
        """Compiles a complete method, function or constructor."""

        # If there are no subroutine declarations, return.
        if not re.match("(constructor|function|method)", self.tokenizer.current_token):
            raise SyntaxError

        # Create a fresh subroutine table.
        self.table.start_subroutine()

        function_type = self.eat("(constructor|function|method)")

        # If it's a method, add 'this' as the first argument.
        if function_type == "method":
            self.table.define("this", self.class_name, "arg")

        self.eat(f"(void|{CompilationEngine.COMMON_PATTERNS['type']})")
        subroutine_name = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])
        self.eat("\(")
        self.compile_parameter_list()
        self.eat("\)")
        self.writer.write_function(f"{self.class_name}.{subroutine_name}", self.table.var_count("arg"))
        self.compile_subroutine_body()


    def compile_parameter_list(self):
        """Compiles a (possibly empty) parameter list. Does not handle the enclosing ()."""

        argument = {"kind": "arg"}

        try: # If the first token does not match, it is an empty parameter list, thus return.
            argument["type"] = self.eat(CompilationEngine.COMMON_PATTERNS["type"])
        except SyntaxError:
            return

        argument["name"] = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])

        # Add the argument to the subroutine table.
        self.table.define(argument["name"], argument["type"], argument["kind"])

        # There can be zero or more additional varNames.
        while True:
            try: # This one is optional. If there is no ',' then stop searching for additional varNames.
                self.eat("\,")
            except SyntaxError:
                break

            try: # This one is mandatory. ',' must be followed by varName.
                argument["type"] = self.eat(CompilationEngine.COMMON_PATTERNS["type"])
                argument["name"] = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])

                # Add the argument to the subroutine table.
                self.table.define(argument["name"], argument["type"], argument["kind"])
            except SyntaxError:
                print("Incorrect syntax.")
                sys.exit(1)



    def compile_subroutine_body(self):
        """Compiles a subroutine's body."""

        self.eat("\{")
        # There can be zero or more variable declarations.
        while True:
            try:
                self.compile_var_dec()
            except SyntaxError:
                break

        self.compile_statements()
        self.eat("\}")


    def compile_var_dec(self):
        """Compiles a var declaration."""

        # If there is no variable decalaration, return.
        if self.tokenizer.current_token != "var":
            raise SyntaxError

        variable = {"kind": "var"}

        self.eat("var")
        variable["type"] = self.eat(CompilationEngine.COMMON_PATTERNS["type"])
        variable["name"] = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])

        # Add the variable to the subroutine table.
        self.table.define(variable["name"], variable["type"], variable["kind"])

        # There can be zero or more additional varNames.
        while True:
            try: # This one is optional. If there is no ',' then stop searching for additional varNames.
                self.eat("\,")
            except SyntaxError:
                break

            try: # This one is mandatory. ',' must be followed by varName.
                variable["name"] = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])

                # Add the variable to the subroutine table.
                self.table.define(variable["name"], variable["type"], variable["kind"])
            except SyntaxError:
                print("Incorrect syntax.")
                sys.exit(1)

        self.eat("\;")


    def compile_statements(self):
        """Compiles a sequence of statements. Does not handle the enclosing {}."""

        while True:
            if self.tokenizer.current_token == "let":
                self.compile_let()
            elif self.tokenizer.current_token == "if":
                self.compile_if()
            elif self.tokenizer.current_token == "while":
                self.compile_while()
            elif self.tokenizer.current_token == "do":
                self.compile_do()
            elif self.tokenizer.current_token == "return":
                self.compile_return()
            else:
                break


    def compile_let(self):
        """Compiles a let statement."""

        self.eat("let")
        var_name = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])
        # Check whether it's an array assignment.
        is_array = True
        try:
            self.eat("\[")
        except SyntaxError:
            is_array = False

        if is_array:
            self.compile_expression()
            self.eat("\]")

        self.eat("\=")
        self.compile_expression()
        self.eat("\;")

        type, kind, index = self.get_symbol_values(var_name)
        if type and kind:
            self.writer.write_pop(kind, index)
        else:
            raise SyntaxError(f"Variable {var_name} is undefined.")


    def compile_if(self):
        """Compiles an if statement, possibly with a trailing else clause."""

        self.eat("if")
        self.eat("\(")
        self.compile_expression()
        self.eat("\)")

        self.writer.write_arithmetic("not")
        self.writer.write_if(f"L{self.label_num}")

        self.eat("\{")
        self.compile_statements()
        self.eat("\}")

        if self.tokenizer.current_token == "else":
            self.writer.write_goto(f"L{self.label_num + 1}")
            self.writer.write_label(f"L{self.label_num}")

            self.eat("else")
            self.eat("\{")
            self.compile_statements()
            self.eat("\}")

            self.writer.write_label(f"L{self.label_num + 1}")
            self.label_num += 2
        else:
            self.writer.write_label(f"L{self.label_num}")


    def compile_while(self):
        """Compiles a while statement."""

        self.writer.write_label(f"L{self.label_num}")

        self.eat("while")
        self.eat("\(")
        self.compile_expression()
        self.eat("\)")

        self.writer.write_arithmetic("not")
        self.writer.write_if(f"L{self.label_num + 1}")

        self.eat("\{")
        self.compile_statements()
        self.eat("\}")

        self.writer.write_goto(f"L{self.label_num}")
        self.writer.write_label(f"{self.label_num + 1}")
        self.label_num += 2


    def compile_do(self):
        """Compiles a do statement."""

        self.eat("do")

        # subroutineCall
        func = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])
        if self.tokenizer.current_token == ".":
            func += self.eat("\.")
            func += self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])
            self.eat("\(")
            num_of_expressions = self.compile_expression_list()
            self.eat("\)")
        elif self.tokenizer.current_token == "(":
            func = f"{self.class_name}.{func}"
            self.eat("\(")
            num_of_expressions = self.compile_expression_list()
            self.eat("\)")
        else:
            print("Syntax error.")
            sys.exit(1)

        self.writer.write_call(func, num_of_expressions)
        self.writer.write_pop("temp", 0) # Dispose of the return value.

        self.eat("\;")


    def compile_return(self):
        """Compiles a return statement."""

        self.eat("return")
        try:
            self.compile_expression()
        except SyntaxError:
            # If there is no return value, return 0.
            self.writer.write_push("constant", 0)
        self.eat("\;")
        self.writer.write_return()


    def compile_expression(self):
        """Compiles an expression."""

        # If there is no expression, return.
        ending_symbols = (")", "]", ";")
        if self.tokenizer.current_token in ending_symbols:
            return

        self.compile_term()

        operators = {
            "+": "add",
            "-": "sub",
            "&": "and",
            "|": "or",
            "<": "lt",
            ">": "gt",
            "=": "eq"
        }

        # A term can be followed by an operator. If so, operator must be followed by another term.
        while True:
            try:
                op = self.eat("(\+|\-|\*|\/|\&|\||\<|\>|\=)")
            except SyntaxError:
                break

            try:
                self.compile_term()

                if op in operators:
                    self.writer.write_arithmetic(operators[op])
                else:
                    if op == "*":
                        self.writer.write_call("Math.multiply", 2)
                    else:
                        self.writer.write_call("Math.divide", 2)
            except SyntaxError:
                print("Syntax error.")
                sys.exit(1)


    def compile_term(self):
        """Compiles a term.
        If the current token is an identifier, the routine must distinguish between a variable,
        an array entry, or a subroutine call."""

        unary_ops = ("~", "-")

        # Check to see whether it's a subroutine call.
        current_token = self.tokenizer.current_token # Save the current token.
        self.tokenizer.advance()
        next_token = self.tokenizer.current_token # Get the next token.
        # If current token is an identifier and next token is '(' or '.' it is a subroutine call.
        if re.match(CompilationEngine.COMMON_PATTERNS["identifier"] ,current_token) and (next_token == "(" or next_token == "."):
            self.tokenizer.current_token = current_token # Restore the current token.

            class_or_function_identifier = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"], advance=False)
            self.tokenizer.current_token = next_token # Set the tokenizer's current token to the previously stored next token.

            if next_token == "(":
                self.eat("\(")
                num_of_expressions = self.compile_expression_list()
                self.eat("\)")

                self.writer.write_call(f"{self.class_name}.{class_or_function_identifier}", num_of_expressions)
            else:
                self.eat("\.")
                function_identfier = self.eat(CompilationEngine.COMMON_PATTERNS["identifier"])
                self.eat("\(")
                num_of_expressions = self.compile_expression_list()
                self.eat("\)")

                self.writer.write_call(f"{class_or_function_identifier}.{function_identfier}", num_of_expressions)

        else:
            self.tokenizer.current_token = current_token # Restore the current token.

            if self.tokenizer.current_token == "(":
                self.eat("\(", advance=False)
                self.tokenizer.current_token = next_token # Set the tokenizer's current token to the previously stored next token.

                self.compile_expression()
                self.eat("\)")
            elif self.tokenizer.current_token in unary_ops:
                op = self.eat("(\~|\-)", advance=False)
                self.tokenizer.current_token = next_token # Set the tokenizer's current token to the previously stored next token.

                self.compile_term()
                self.writer.write_arithmetic("not" if op == "~" else "neg")

            else:
                # Specific pattern for string constants
                if "\"" in self.tokenizer.current_token:
                    self.eat("^\".*\"", advance=False)
                else:
                    identifier = self.eat(f"({CompilationEngine.COMMON_PATTERNS['identifier']}|[0-9]+)", advance=False)

                    if identifier.isdigit():
                        self.writer.write_push("constant", identifier)
                    else:
                        type, kind, index = self.get_symbol_values(identifier)

                        # If identifier is not in the symbol table, it can be assumed it is a subroutine name or a class name.
                        if type and kind:
                            self.writer.write_push(kind, index)

                self.tokenizer.current_token = next_token # Set the tokenizer's current token to the previously stored next token.

                if self.tokenizer.current_token == "[":
                    self.eat("\[")
                    self.compile_expression()
                    self.eat("\]")


    def compile_expression_list(self):
        """Compiles a (possibly empty) comma-separated list of expressions."""

        num_of_expressions = 0

        try:
            self.compile_expression()
            num_of_expressions += 1
        except:
            return num_of_expressions

        while True:
            try:
                self.eat("\,")
            except SyntaxError:
                break

            self.compile_expression()
            num_of_expressions += 1

        return num_of_expressions


    def eat(self, re_pattern, advance=True):
        # Writes the word to the output xml file.
        print(f"Pattern: {re_pattern} , Token: {self.tokenizer.current_token}")

        if not re.match(re_pattern, self.tokenizer.current_token):
            print(f"Token {self.tokenizer.current_token} doesn't match the pattern {re_pattern}")
            raise SyntaxError(f"Token {self.tokenizer.current_token} does not match the pattern {re_pattern}.")
        else:
            token_type = self.tokenizer.token_type()
            token = self.tokenizer.current_token

            if advance: # Advance will be false only if term is a subroutine call.
                self.tokenizer.advance()

            return token


    def var_already_defined(self, var_name):
        if self.table.index_of(var_name) != None:
            return True
        else:
            return False


    def get_symbol_values(self, symbol_name):
        type = self.table.type_of(symbol_name)
        kind = self.table.kind_of(symbol_name)
        index = self.table.index_of(symbol_name)

        return type, kind, index
