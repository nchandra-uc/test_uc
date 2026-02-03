"""
Helobalwan Module

A module for helobalwan functionality.
"""


class Helobalwan:
    """Main Helobalwan class."""
    
    def __init__(self):
        """Initialize Helobalwan instance."""
        self.name = "helobalwan"
    
    def hello(self):
        """Return a hello message."""
        return f"Hello from {self.name}!"
    
    def process(self, data=None):
        """Process data."""
        if data is None:
            return "No data provided"
        return f"Processing: {data}"


def main():
    """Main function for testing."""
    helo = Helobalwan()
    print(helo.hello())
    print(helo.process("test data"))


if __name__ == "__main__":
    main()
