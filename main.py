import pandas as pd
import random
from collections import Counter

# Φόρτωση δεδομένων από CSV
data = pd.read_csv("data/joker_results.csv")

# Ανάλυση αριθμών
main_numbers = data[['main1', 'main2', 'main3', 'main4']].values.flatten()
joker_numbers = data['joker'].values

main_freq = Counter(main_numbers)
joker_freq = Counter(joker_numbers)

# Επιλογή των πιο συχνών αριθμών
top_main = [num for num, _ in main_freq.most_common(15)]
top_joker = [num for num, _ in joker_freq.most_common(5)]

# Δημιουργία 5 προβλέψεων με αιτιολόγηση
predictions = []
justifications = []

for i in range(5):
    main_comb = sorted(random.sample(top_main, 4))
    joker_pick = random.choice(top_joker)
    predictions.append((main_comb, joker_pick))

    justification = [f"{num} εμφανίστηκε {main_freq[num]} φορές" for num in main_comb]
    justification.append(f"Joker {joker_pick} εμφανίστηκε {joker_freq[joker_pick]} φορές")
    justifications.append(justification)

# Εμφάνιση προβλέψεων
for idx, ((main_comb, joker_pick), justification) in enumerate(zip(predictions, justifications), 1):
    print(f"\n✅ Prediction {idx}: {main_comb} + Joker {joker_pick}")
    for reason in justification:
        print(f"   - {reason}")

# Τελικός συνδυασμός βάσει συχνότητας από τις 5 προβλέψεις
all_main = [num for pred in predictions for num in pred[0]]
all_jokers = [pred[1] for pred in predictions]

final_main = sorted([num for num, _ in Counter(all_main).most_common(4)])
final_joker = Counter(all_jokers).most_common(1)[0][0]

print("\n🎯 Τελικός Συνδυασμός (βάσει συχνότητας από τις 5 προβλέψεις):")
print(f"   ➤ {final_main} + Joker {final_joker}")
