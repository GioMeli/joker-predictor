import os
import hashlib
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

def evaluate_prediction(predicted_main, predicted_joker, actual_main, actual_joker):
    matched_main = len(set(predicted_main) & set(actual_main))
    matched_joker = int(predicted_joker == actual_joker)
    return matched_main, matched_joker

def generate_prediction(df, num_predictions=5, seed_source="", actual_draw=None):
    seed = int(hashlib.md5(seed_source.encode()).hexdigest(), 16) % (2**32)
    random.seed(seed)

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
    seen_combinations = set()

    for _ in range(num_predictions):
        attempt = 0
        while attempt < 100:
            selected_main = []
            used_decades = Counter()
            candidates = hot_main + cold_main
            random.shuffle(candidates)
            for num in candidates:
                decade = get_decade(num)
                if used_decades[decade] < 2:
                    selected_main.append(num)
                    used_decades[decade] += 1
                if len(selected_main) == 5:
                    break
            if len(selected_main) < 5:
                attempt += 1
                continue
            selected_main = sorted(selected_main)
            total_sum = sum(selected_main)
            if not (MIN_SUM <= total_sum <= MAX_SUM):
                attempt += 1
                continue
            selected_joker = int(random.choice(hot_joker + cold_joker))
            combo_key = tuple(selected_main + [selected_joker])
            if combo_key not in seen_combinations:
                seen_combinations.add(combo_key)
                predictions.append((selected_main, selected_joker))
                break
            attempt += 1

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

    accuracy_report = []
    if actual_draw:
        actual_main, actual_joker = actual_draw
        for combo, joker in predictions:
            matched_main, matched_joker = evaluate_prediction(combo, joker, actual_main, actual_joker)
            accuracy_report.append({
                "prediction": combo,
                "joker": joker,
                "matched_main": matched_main,
                "matched_joker": matched_joker
            })

    return predictions, (final_main, final_joker), accuracy_report

@app.route('/', methods=['GET', 'POST'])
def index():
    predictions = []
    final_combination = None
    accuracy_report = []
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            df = load_data(filepath)
            seed_source = file.filename
        else:
            df = load_data("data/joker_results_updated.csv")
            seed_source = "default"

        # Προαιρετικά: ορισμός της τελευταίας πραγματικής κλήρωσης για αξιολόγηση
        actual_draw = ([2, 10, 16, 21, 40], 15)

        predictions, final_combination, accuracy_report = generate_prediction(
            df, seed_source=seed_source, actual_draw=actual_draw
        )

    return render_template('index.html',
                           predictions=predictions,
                           final=final_combination,
                           main_chart="main_number_frequencies.png",
                           joker_chart="joker_number_frequencies.png",
                           accuracy=accuracy_report)

if __name__ == '__main__':
    app.run(debug=True)

