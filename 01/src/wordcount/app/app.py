import os

from strands import Agent, tool
from strands.vended_tools import file_editor, shell, sleep
from strands.models.ollama import OllamaModel
from datetime import datetime

@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word (str): The input word to search in
        letter (str): The specific letter to count

    Returns:
        int: The number of occurrences of the letter in the word
    """
    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")

    return word.lower().count(letter.lower())


model = OllamaModel(
    host=os.environ.get("OLLAMA_HOST", "http://ollama:11434"),
    model_id="llama3.1",
)
agent = Agent(model=model,
tools=[letter_counter, file_editor, shell])
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    agent(f'How many letter R\'s are in the word "strawberry"? Write the answer to answer_{timestamp}.txt. then pause for two seconds. then run "cat answer_{timestamp}.txt" to see the result.')
