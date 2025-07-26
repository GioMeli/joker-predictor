
import pandas as pd
from collections import Counter

def load_data(csv_path="data/joker_results.csv"):
    df = pd.read_csv(csv_path)
    return df

def analyze_frequencies(df):
    main_numbers = df[["Num1", "Num2", "Num3", "Num4"]].values.flatten()
    joker_numbers = df["Joker"].values

    main_counter = Counter(main_numbers)
    joker_counter = Counter(joker_numbers)

    main_freq = sorted(main_counter.items(), key=lambda x: x[1], reverse=True)
    joker_freq = sorted(joker_counter.items(), key=lambda x: x[1], reverse=True)

    return main_freq, joker_freq

def get_hot_and_cold(freq_list, top_n=10):
    hot = freq_list[:top_n]
    cold = freq_list[-top_n:]
    return hot, cold

if __name__ == "__main__":
    df = load_data()
    main_freq, joker_freq = analyze_frequencies(df)

    hot_main, cold_main = get_hot_and_cold(main_freq)
    hot_joker, cold_joker = get_hot_and_cold(joker_freq)

    print("🔥 Hot Main Numbers:", hot_main)
    print("❄️ Cold Main Numbers:", cold_main)
    print("🔥 Hot Joker Numbers:", hot_joker)
    print("❄️ Cold Joker Numbers:", cold_joker)

