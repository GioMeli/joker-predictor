import random
from src.analyze import load_data, analyze_frequencies, get_hot_and_cold

def generate_prediction(df, num_predictions=5):
    main_freq, joker_freq = analyze_frequencies(df)
    hot_main, _ = get_hot_and_cold(main_freq, top_n=20)
    hot_joker, _ = get_hot_and_cold(joker_freq, top_n=5)

    hot_main_numbers = [int(num) for num, _ in hot_main]
    hot_joker_numbers = [int(num) for num, _ in hot_joker]

    predictions = []
    for _ in range(num_predictions):
        selected = random.sample(hot_main_numbers, 3)
        remaining = list(set(range(1, 46)) - set(selected))
        balanced = [n for n in remaining if (n <= 22 and sum(x <= 22 for x in selected) < 2) or (n > 22 and sum(x > 22 for x in selected) < 2)]
        selected += random.sample(balanced, 1)
        selected = sorted(selected)
        joker = random.choice(hot_joker_numbers)
        predictions.append((selected, joker))
    return predictions

