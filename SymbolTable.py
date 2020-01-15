class SymbolTable:

    STATIC_COUNT = 0
    FIELD_COUNT = 0
    LOCAL_COUNT = 0
    ARG_COUNT = 0

    def __init__(self):
        self.class_table = {}
        self.subroutine_table = {}


    def start_subroutine(self):
        """Starts a new subroutine scope (i.e., resets the subroutine's symbol table.)"""

        self.subroutine_table = {}
        SymbolTable.LOCAL_COUNT = 0
        SymbolTable.ARG_COUNT = 0


    def define(self, name, type, kind):
        """Defines a new identifier of the given name, type and kind, and assigns it a running index.
        STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope."""

        if kind == "static":
            self.class_table[name] = {
            "type": type,
            "kind": "static",
            "index": SymbolTable.STATIC_COUNT
            }

            SymbolTable.STATIC_COUNT += 1
        elif kind == "field":
            self.class_table[name] = {
            "type": type,
            "kind": "field",
            "index": SymbolTable.FIELD_COUNT
            }

            SymbolTable.FIELD_COUNT += 1
        elif kind == "var":
            self.subroutine_table[name] = {
            "type": type,
            "kind": "local",
            "index": SymbolTable.LOCAL_COUNT
            }

            SymbolTable.LOCAL_COUNT += 1
        elif kind == "arg":
            self.subroutine_table[name] = {
            "type": type,
            "kind": "argument",
            "index": SymbolTable.ARG_COUNT
            }

            SymbolTable.ARG_COUNT += 1


    def var_count(self, kind):
        """Returns the number of variables of the given kind already defined in the current scope."""

        numbers = {"static": SymbolTable.STATIC_COUNT, "field": SymbolTable.FIELD_COUNT, "var": SymbolTable.LOCAL_COUNT, "arg": SymbolTable.ARG_COUNT}

        return numbers[kind]


    def kind_of(self, name):
        """Returns the kind of the named identifier in the current scope. If the identifier is unknown in the current scope, returns None."""

        return self.get_value(name, "kind")


    def type_of(self, name):
        """Returns the type of the named identifier in the current scope."""

        return self.get_value(name, "type")


    def index_of(self, name):
        """Returns the index assigned to the named identifier."""

        return self.get_value(name, "index")


    def get_value(self, name, type_of_value):
        if name in self.class_table:
            return self.class_table[name][type_of_value]
        elif name in self.subroutine_table:
            return self.subroutine_table[name][type_of_value]
        else:
            return None
