# logic.py
# This file contains the "engine" that interacts with the rules.
# It manages the state of the decision-making process.

# Import standard library helpers
import re
import string

# Import the data structures from our rules file
from rules import LOOKUP_TABLE, DECISION_TREE


def _normalize_noun(noun):
    """Return a canonical form of ``noun`` for lookup-table comparisons."""
    if noun is None:
        return ""

    normalized = str(noun).strip()
    normalized = re.sub(r"^(?:the|an|a)\s+", "", normalized, flags=re.IGNORECASE)
    normalized = normalized.translate(str.maketrans("", "", string.punctuation))
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized.lower()

class ArticleLogic:
    """
    Manages the logic flow for determining the correct English article.
    It holds the current state of the user's path through the decision tree.
    """
    def __init__(self):
        """Initializes the logic controller."""
        self.current_node_id = "start"

    def reset(self):
        """Resets the logic to the beginning of the decision tree."""
        self.current_node_id = "start"

    def check_lookup_table(self, noun):
        """
        First check: See if the noun is a special case in our LOOKUP_TABLE.
        Args:
            noun (str): The raw user-provided noun or phrase.
        Returns:
            dict: The result dictionary if found, otherwise None.
        """
        normalized = _normalize_noun(noun)
        if not normalized:
            return None

        return LOOKUP_TABLE.get(normalized)

    def get_current_node(self):
        """
        Retrieves the data for the current node in the decision tree.
        Returns:
            dict: The dictionary of the current node.
        """
        return DECISION_TREE[self.current_node_id]

    def process_answer(self, selected_option_text):
        """
        Processes the user's answer and moves to the next node in the tree.
        Args:
            selected_option_text (str): The text from the button the user clicked.
        Returns:
            dict: The data for the *next* node in the decision tree.
        """
        # Find the current node
        current_node = self.get_current_node()
        
        # Look up the next node's ID based on the user's choice
        next_node_id = current_node["options"][selected_option_text]
        
        # Update the state to the new node
        self.current_node_id = next_node_id
        
        # Return the data for the new node
        return self.get_current_node()

# --- This section is for testing our logic directly ---
def test_logic():
    """A simple text-based simulation to ensure our logic works."""
    print("--- Testing ArticleLogic ---")
    
    # 1. Test the lookup table (with normalization for determiners/punctuation)
    print("\n[Test 1: Lookup Table]")
    logic_engine = ArticleLogic()
    lookup_samples = [
        "USA",
        "the USA",
        "an opera",
    ]
    for sample in lookup_samples:
        result = logic_engine.check_lookup_table(sample)
        if result:
            print(f"Checked '{sample}': Found in lookup table!")
            print(f"  -> Article: {result['article']}")
            print(f"  -> Explanation: {result['explanation']}")
        else:
            print(f"Checked '{sample}': Not in lookup table. Starting tree...")

    # 2. Test the decision tree flow
    print("\n[Test 2: Decision Tree Walkthrough]")
    logic_engine.reset() # Start from the beginning
    
    # Step 1: Get starting question
    current_node = logic_engine.get_current_node()
    print(f"Q: {current_node['question']}")
    options = list(current_node['options'].keys())
    print(f"Options: {options}")
    
    # Step 2: Simulate user choosing the first option
    user_choice = options[0]
    print(f"\nUser chooses: '{user_choice}'")
    current_node = logic_engine.process_answer(user_choice)
    
    # Step 3: See the next question or result
    if "question" in current_node:
        print(f"Q: {current_node['question']}")
        options = list(current_node['options'].keys())
        print(f"Options: {options}")
    elif "article" in current_node:
        print(f"\nFinal Result Reached!")
        print(f"  -> Article: {current_node['article']}")
        print(f"  -> Explanation: {current_node['explanation']}")

if __name__ == "__main__":
    # This block runs ONLY when you execute `python logic.py` directly.
    # It allows us to test our logic before building the GUI.
    test_logic()

