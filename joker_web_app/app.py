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

def get_decade(num):
    return (num - 1) // 10

def generate_prediction(df, num_predictions=5):
    main_counter, joker_counter = analyze_frequencies(df)

    plot_frequencies(main_counter, "Main Number Frequencies", "main_number_frequencies.png")
    plot_frequencies(joker_counter, "Joker Number Frequencies", "joker_number_frequencies.png")

    sorted_main = sorted(main_counter.items(), key=lambda x: x[1], reverse=True)
    sorted_joker = sorted(joker_counter.items(), key=lambda x: x[1], reverse=True)

    hot_main = [int(num) for num, _ in sorted_main[:25]]
    cold_main = [int(num) for num, _ in sorted_main[-25:]]
    hot_joker = [int(num) for num, _ in sorted_joker[:5]]
    cold_joker = [int(num) for num, _ in sorted_joker[-5:]]

    MIN_SUM = 100
    MAX_SUM = 160

    predictions = []
    for _ in range(num_predictions):
        while True:
            selected_main = []
            used_decades = set()
            candidates = hot_main + cold_main
            random.shuffle(candidates)
            for num in candidates:
                decade = get_decade(num)
                if decade not in used_decades:
                    selected_main.append(num)
                    used_decades.add(decade)
                if len(selected_main) == 5:
                    break
            if len(selected_main) < 5:
                continue
            selected_main = sorted(selected_main)
            total_sum = sum(selected_main)
            if MIN_SUM <= total_sum <= MAX_SUM:
                break
        selected_joker = int(random.choice(hot_joker + cold_joker))
        predictions.append((selected_main, selected_joker))

    all_main = [num for combo, _ in predictions for num in combo]
    all_jokers = [joker for _, joker in predictions]
    final_main = sorted([int(num) for num, _ in Counter(all_main).most_common(5)])
    final_joker = int(Counter(all_jokers).most_common(1)[0][0])

    # Ισορροπία μονών/ζυγών
    odd_count = sum(1 for n in final_main if n % 2 == 1)
    even_count = 5 - odd_count
    if abs(odd_count - even_count) > 2:
        for num in hot_main + cold_main:
            if num not in final_main:
                if odd_count > even_count and num % 2 == 0:
                    final_main[-1] = num
                    break
                elif even_count > odd_count and num % 2 == 1:
                    final_main[-1] = num
                    break
        final_main = sorted(final_main)

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

