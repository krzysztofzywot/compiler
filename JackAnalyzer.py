import sys
import glob
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from SymbolTable import SymbolTable
from VMWriter import VMWriter


def main():
    # Quit if no file name has been provided or if the file extension isn't .jack
    if len(sys.argv) == 1:
        print("You must provide a valid jack file or directory name.")
        sys.exit(1)

    user_input = sys.argv[1]

    files_to_translate = []
    is_directory = ".jack" not in user_input
    # If user provided directory name, iterate over each jack file in it and add it's name to the list
    if is_directory:
        try:
            for file_name in glob.glob(f"{user_input}/*.jack"):
                files_to_translate.append(file_name)
        except FileNotFoundError:
            sys.exit(1)
    else:
        files_to_translate.append(user_input)

    for file in files_to_translate:
        tokenizer = JackTokenizer(file)
        symbol_table = SymbolTable()
        vmwriter = VMWriter(file)
        compilator = CompilationEngine(tokenizer, symbol_table, vmwriter)
        # compilator = CompilationEngineCOPY(file, tokenizer, symbol_table)

    tokenizer.close()


if __name__ == "__main__":
    main()
