import random
from collections import Counter

def generate_combination():
    """Generate a combination of 5 unique numbers (1-45) and 1 Joker number (1-20)."""
    numbers = sorted(random.sample(range(1, 46), 5))
    joker = random.randint(1, 20)
    return numbers, joker

def generate_predictions(n=5):
    """Generate n predictions of 5 numbers + 1 Joker."""
    predictions = []
    for _ in range(n):
        numbers, joker = generate_combination()
        predictions.append((numbers, joker))
    return predictions

def generate_final_combination(predictions):
    """Generate a final combination based on the most frequent numbers and jokers."""
    all_numbers = []
    all_jokers = []

    for numbers, joker in predictions:
        all_numbers.extend(numbers)
        all_jokers.append(joker)

    most_common_numbers = [num for num, _ in Counter(all_numbers).most_common(5)]
    most_common_joker = Counter(all_jokers).most_common(1)[0][0]

    return sorted(most_common_numbers), most_common_joker
