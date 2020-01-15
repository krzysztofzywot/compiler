class VMWriter:

    def __init__(self, fname):
        try:
            self.f = open(fname.replace(".jack", ".vm"), "w")
        except IOError:
            raise IOError


    def write_push(self, segment, index):
        """Writes a VM push command."""

        self.f.write(f"push {segment} {index}\n")


    def write_pop(self, segment, index):
        """Writes a VM pop command."""

        self.f.write(f"pop {segment} {index}\n")


    def write_arithmetic(self, command):
        """Writes a VM arithmentic-logical command."""

        self.f.write(f"{command}\n")


    def write_label(self, label):
        """Writes a VM label command."""

        self.f.write(f"label {label}\n")


    def write_goto(self, label):
        """Writes a VM goto command."""

        self.f.write(f"goto {label}\n")


    def write_if(self, label):
        """Writes a VM if-goto command."""

        self.f.write(f"if-goto {label}\n")


    def write_call(self, name, nargs):
        """Writes a VM call command."""

        self.f.write(f"call {name} {nargs}\n")


    def write_function(self, name, nlocals):
        """Writes a VM function command."""

        self.f.write(f"function {name} {nlocals}\n")


    def write_return(self):
        """Writes a VM return command."""

        self.f.write("return\n")


    def close(self):
        """Closes the output file."""

        self.f.close()
