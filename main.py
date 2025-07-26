from src.analyze import load_data
from src.predict import generate_prediction

def main():
    df = load_data()
    predictions = generate_prediction(df)
    print("Top 5 predicted combinations:")
    for i, (numbers, joker) in enumerate(predictions, 1):
        print(f"{i}. Numbers: {numbers} | Joker: {joker}")

if __name__ == "__main__":
    main()

