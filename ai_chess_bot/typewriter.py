import time

def typewriter(text, delay=0.05):
    """
    Print text like a typewriter, character by character.
    
    :param text: String to print
    :param delay: Seconds to wait between each character
    """
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # newline at the end