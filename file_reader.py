import json

class FileReader:
    def load_json(self, json_file_path):
        with open(json_file_path, "r") as file:
            data = json.load(file)
            return data

    def load_text_to_array(self, file_path):
        array = []
        with open(file_path, "r") as file:
            for line in file:
                # Remove leading and trailing whitespaces, then convert to the appropriate data type
                element = line.strip()
                try:
                    element = eval(element)  # Try to evaluate the string as a literal (e.g., int, float)
                except (NameError, SyntaxError):
                    pass  # If not a literal, keep it as a string
                array.append(element)
        return array