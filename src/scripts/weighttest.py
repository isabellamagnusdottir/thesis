from fractions import Fraction
import random as rand


def try_weights(weights):
    if rand.choices([True, False], weights)[0]:
        return rand.randint(0, 30)
    return rand.randint(-10, -1)


if __name__ == "__main__":
    
    asdf = [try_weights([80, 20]) for _ in range(10000)]
    positive_count = 0
    negative_count = 0
    for v in asdf:
        if v < 0:
            negative_count += 1
        else:
            positive_count += 1

    ratio = positive_count/negative_count

    print(f"Positive: {positive_count}, Negative: {negative_count}, Ratio: {ratio}")