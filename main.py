from src.predict import generate_predictions, generate_final_combination

def main():
    predictions = generate_predictions()
    print("Top 5 predicted combinations:")
    for i, (numbers, joker) in enumerate(predictions, 1):
        print(f"{i}. Numbers: {numbers} | Joker: {joker}")

    final_numbers, final_joker = generate_final_combination(predictions)
    print("\nFinal Combination:")
    print(f"Numbers: {final_numbers} | Joker: {final_joker}")

if __name__ == "__main__":
    main()

