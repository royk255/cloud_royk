import os

class TextFileManager:
    def __init__(self, file_path=None):
        # Set default file path if none is provided
        if file_path is None:
            file_path = os.path.join(os.getcwd(), 'projects_file.txt')
        self.file_path = file_path
        # Ensure the file exists
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                pass

    def add_line(self, line):
        """Add a line to the text file."""
        with open(self.file_path, 'a') as f:
            f.write(line + '\n')

    def get_line_by_last_part(self, last_part):
        """Get a line that ends with the specified last part."""
        with open(self.file_path, 'r') as f:
            for line in f:
                if line.rstrip().endswith("\\" + last_part) or line.rstrip().endswith("//" + last_part):
                    return line.rstrip()
        return None

    def remove_line_by_filter(self, filter_text):
        """Remove all lines containing the specified filter text."""
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
        with open(self.file_path, 'w') as f:
            for line in lines:
                if filter_text not in line:
                    f.write(line)

    
