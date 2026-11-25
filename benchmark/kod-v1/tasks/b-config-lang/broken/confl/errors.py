class ConfigError(ValueError):
    """Syntax or structure error with a 1-based source position."""

    def __init__(self, message, line, column):
        super().__init__(f"{message} (line {line}, column {column})")
        self.message = message
        self.line = line
        self.column = column
