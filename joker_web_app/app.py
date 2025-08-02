import os
from flask import Flask, request, render_template
import pandas as pd
from collections import Counter
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

    birthday_numbers = set(range(1, 32)) | set(range(1, 13))
    MIN_SUM = 100
    MAX_SUM = 160

    # Επιλογή των 5 πιο συχνούς αριθμών
    selected_main = sorted([num for num, _ in sorted_main[:5]])
    total_sum = sum(selected_main)

    # Αν δεν πληροί τα κριτήρια, δοκιμάζουμε με άλλους από τους cold
    if not (MIN_SUM <= total_sum <= MAX_SUM):
        selected_main = sorted(cold_main[:5])
        total_sum = sum(selected_main)

    # Επιλογή του πιο συχνού Τζόκερ
    selected_joker = sorted_joker[0][0]

    predictions = [(selected_main, selected_joker)]
    return predictions, (selected_main, selected_joker)

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

