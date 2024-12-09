from datetime import datetime

def print_debug(category: str, message: str, is_interim: bool = False) -> None:
    """
    print formatted debug messages with timestamps and color coding for different categories
    """
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    # color codes for different message categories
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    GRAY = "\033[90m"
    RESET = "\033[0m"

    category_color = {
        "SYSTEM": BLUE,  # system messages and errors
        "USER": GREEN,   # user speech transcriptions
        "LLM": YELLOW,   # llm responses
        "DEBUG": GRAY    # debug information
    }

    color = category_color.get(category, RESET)

    # print interim messages with carriage return for updates
    if is_interim:
        print(f"{color}[{timestamp}] [{category}] (interim) {message}{RESET}", end="\r")
    else:
        print(f"{color}[{timestamp}] [{category}] {message}{RESET}")
