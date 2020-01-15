import re


class JackTokenizer:

    KEYWORDS = (
        "class",
        "constructor",
        "function",
        "method",
        "field",
        "static",
        "var",
        "int",
        "char",
        "boolean",
        "void",
        "true",
        "false",
        "null",
        "this",
        "let",
        "do",
        "if",
        "else",
        "while",
        "return"
    )

    SYMBOLS = (
        "\{",
        "\}",
        "\(",
        "\)",
        "\[",
        "\]",
        "\.",
        "\,",
        "\;",
        "\+",
        "\-",
        "\*",
        "\/",
        "\&",
        "\|",
        "\<",
        "\>",
        "\=",
        "\~"
    )

    SYMBOL_REPLACEMENTS = {
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "&": "&amp;"
    }

    def __init__(self, fname):
        try:
            self.f = open(fname, "r")
        except IOError:
            raise IOError

        self.current_token = ""

        self.content = self.f.read()
        self.content = self.content.strip()
        self.symbols_regex = "|".join(JackTokenizer.SYMBOLS)


    def has_more_tokens(self):
        """Are there more tokens in the input?"""

        if not self.content:
            return False
        return True


    def advance(self):
        """Gets the next token from the input, and makes it the current token.
        This method should be called only if has_more_tokens is true.
        Initially there is no current token."""

        # Keys are substring start indexes and value are match objects.
        matches_dict = {}
        comment_dict = {} # A separate dictionary for comments.

        # This pattern will search for string constants ie. "hello world".
        self.get_match_index(re.compile("\"[^\"]*\""), matches_dict)

        # This pattern will search for keywords, integers, variables and symbols.
        self.get_match_index(re.compile(f"([a-zA-Z0-9]+|{self.symbols_regex})"), matches_dict)

        # This pattern will search for comments.
        self.get_match_index(re.compile("(/{2}[\s\w\W]*?\n+|/\*\*[\s\w\W]*?\*/)"), comment_dict)

        # Sorted matches from lowest to highest start index as a list of tuples.
        sorted_matches = sorted(matches_dict.items(), key=lambda kv: kv[0])

        # Get the best match object (the one with the lowest start index).
        best_match_index = sorted_matches[0][0]
        best_match_object = sorted_matches[0][1]

        comment_index = list(comment_dict.items())[0][0]
        comment_object = list(comment_dict.items())[0][1]

        # Check whether the best match is a comment. If so cut it from the content and advance the tokenizer again.
        # Otherwise just cut the content and set a new current_token.
        if comment_index <= best_match_index and comment_index != 999999:
            self.slice_content(comment_object.end())
            self.advance()
        elif best_match_index != 999999:
            self.slice_content(best_match_object.end())
            self.current_token = best_match_object.group()
        else:
            self.content = ""


    def token_type(self):
        """Returns the type of the current token."""

        if self.current_token in JackTokenizer.KEYWORDS:
            return "KEYWORD"
        elif "\\" + self.current_token in JackTokenizer.SYMBOLS:
            return "SYMBOL"
        elif self.current_token.isdigit() and int(self.current_token) <= 32767:
            return "INT_CONST"
        elif "\"" in self.current_token:
            return "STRING_CONST"
        else:
            return "IDENTIFIER"


    def keyword(self):
        """Returns the keyword which is the current token.
        This method should be called only if token_type is KEYWORD."""

        return self.current_token


    def symbol(self):
        """Returns the character which is the current token.
        Should be called only if token_type is SYMBOL."""

        if self.current_token in JackTokenizer.SYMBOL_REPLACEMENTS:
            return JackTokenizer.SYMBOL_REPLACEMENTS[self.current_token]
        else:
            return self.current_token


    def identifier(self):
        """Returns the identifier which is the current token.
        Should be called only if token_type is IDENTIFIER."""

        return self.current_token


    def int_val(self):
        """Returns the integer value which is the current token.
        Should be called only if token_type is INT_CONST."""

        return str(self.current_token)


    def str_val(self):
        """Returns the string value which is the current token.
        Should be called only if token_type is STR_CONST."""

        return self.current_token.replace("\"", "")


    def get_match_index(self, pattern, dict):
        # Gets the match object based on the given pattern and puts it into the dictionary.
        # If match is not found it puts the value of 999999 as the start index.

        matches = pattern.finditer(self.content)
        match_object = next((x for x in matches), None) # Get the first match object from string pattern matches.
        if match_object:
            dict[match_object.start()] = match_object
        else:
            dict[999999] = None


    def slice_content(self, index):
        try:
            self.content = self.content[index:] # Cut the current token from the content.
        except IndexError: # If there are no tokens left, set self.content to an empty string.
            self.content = ""


    def close(self):
        self.f.close()
