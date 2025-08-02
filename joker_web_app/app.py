import os
from flask import Flask, request, render_template
import pandas as pd
from collections import Counter
import random
import matplotlib.pyplot as plt

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_data(csv_path):
    return pd.read_csv(csv_path)

def analyze_frequencies(df):
    main_numbers = df[["Num1", "Num2", "Num3", "Num4", "Num5"]].values.flatten()
    joker_numbers = df["Joker"].values
    main_counter = Counter(main_numbers)
    joker_counter = Counter(joker_numbers)
    return main_counter, joker_counter

def plot_frequencies(counter, title, filename):
    items = sorted(counter.items())
    numbers = [item[0] for item in items]
    frequencies = [item[1] for item in items]

    plt.figure(figsize=(10, 5))
    plt.bar(numbers, frequencies, color='skyblue')
    plt.title(title)
    plt.xlabel('Number')
    plt.ylabel('Frequency')
    plt.xticks(numbers, rotation=90)
    plt.tight_layout()
    plt.savefig(f"static/{filename}")
    plt.close()

def generate_prediction(df, num_predictions=5):
    main_counter, joker_counter = analyze_frequencies(df)

    # Δημιουργία γραφημάτων
    plot_frequencies(main_counter, "Main Number Frequencies", "main_number_frequencies.png")
    plot_frequencies(joker_counter, "Joker Number Frequencies", "joker_number_frequencies.png")

    sorted_main = sorted(main_counter.items(), key=lambda x: x[1], reverse=True)
    sorted_joker = sorted(joker_counter.items(), key=lambda x: x[1], reverse=True)

    hot_main = [int(num) for num, _ in sorted_main[:25]]
    cold_main = [int(num) for num, _ in sorted_main[-25:]]
    hot_joker = [int(num) for num, _ in sorted_joker[:5]]
    cold_joker = [int(num) for num, _ in sorted_joker[-5:]]

    hot_main_weights = [main_counter[num] for num in hot_main]
    cold_main_weights = [main_counter[num] for num in cold_main]
    hot_joker_weights = [joker_counter[num] for num in hot_joker]
    cold_joker_weights = [joker_counter[num] for num in cold_joker]

    birthday_numbers = set(range(1, 32)) | set(range(1, 13))
    MIN_SUM = 100
    MAX_SUM = 160

    predictions = []
    for _ in range(num_predictions):
        while True:
            weighted_hot_main = hot_main + [num for num in hot_main if num not in birthday_numbers]
            weighted_cold_main = cold_main + [num for num in cold_main if num not in birthday_numbers]
            weighted_hot_weights = hot_main_weights + [main_counter[num] for num in hot_main if num not in birthday_numbers]
            weighted_cold_weights = cold_main_weights + [main_counter[num] for num in cold_main if num not in birthday_numbers]

            selected = sorted(
                random.choices(weighted_hot_main, weights=weighted_hot_weights, k=3) +
                random.choices(weighted_cold_main, weights=weighted_cold_weights, k=2)
            )
            if MIN_SUM <= sum(selected) <= MAX_SUM:
                break

        joker_pool = hot_joker + cold_joker
        joker_weights = hot_joker_weights + cold_joker_weights
        joker = random.choices(joker_pool, weights=joker_weights, k=1)[0]

        predictions.append((selected, joker))

    all_main = [num for combo, _ in predictions for num in combo]
    all_jokers = [joker for _, joker in predictions]

    final_main = sorted([num for num, _ in Counter(all_main).most_common(5)])
    final_joker = Counter(all_jokers).most_common(1)[0][0]

    return predictions, (final_main, final_joker)

@app.route('/', methods=['GET', 'POST'])
def index():
    predictions = []
    final_combination = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            df = load_data(filepath)
        else:
            df = load_data("data/joker_results_updated.csv")

        predictions, final_combination = generate_prediction(df)

    return render_template('index.html', predictions=predictions, final=final_combination,
                           main_chart="main_number_frequencies.png",
                           joker_chart="joker_number_frequencies.png")

if __name__ == '__main__':
    app.run(debug=True)
