import os
from flask import Flask, request, render_template
import pandas as pd
from collections import Counter
import random

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
    return sorted(main_counter.items(), key=lambda x: x[1], reverse=True), sorted(joker_counter.items(), key=lambda x: x[1], reverse=True)

def generate_prediction(df, num_predictions=5):
    main_freq, joker_freq = analyze_frequencies(df)

    hot_main = [int(num) for num, _ in main_freq[:25]]
    cold_main = [int(num) for num, _ in main_freq[-25:]]
    hot_joker = [int(num) for num, _ in joker_freq[:5]]
    cold_joker = [int(num) for num, _ in joker_freq[-5:]]

    # Αριθμοί που αντιστοιχούν σε γενέθλια (ημέρες και μήνες)
    birthday_numbers = set(range(1, 32)) | set(range(1, 13))

    # Όρια αθροίσματος για αποφυγή ακραίων συνδυασμών
    MIN_SUM = 100
    MAX_SUM = 160

    predictions = []
    for _ in range(num_predictions):
        while True:
            # Ενίσχυση πιθανότητας μη γενεθλιακών αριθμών
            weighted_hot_main = hot_main + [num for num in hot_main if num not in birthday_numbers]
            weighted_cold_main = cold_main + [num for num in cold_main if num not in birthday_numbers]

            selected = sorted(random.sample(weighted_hot_main, 3) + random.sample(weighted_cold_main, 2))
            if MIN_SUM <= sum(selected) <= MAX_SUM:
                break

        joker = random.choice(hot_joker + cold_joker)
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

    return render_template('index.html', predictions=predictions, final=final_combination)

if __name__ == '__main__':
    app.run(debug=True)
