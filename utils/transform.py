import pandas as pd

class Transform:

    def __init__(self) -> None:
        return None

    def capital_letters(name) ->str:
        """
        Converts the input string to uppercase and ensures there is only one space between words.

        Args:
            name (str): The input string to be converted to uppercase.

        Returns:
            str: A new string with all characters in uppercase and only one space between words.
        """
        new_name = str(name).upper()
        words = new_name.split()
        cleaned_name = ' '.join(words)

        return cleaned_name
