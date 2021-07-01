from pickle import load, dump

with open("high_score.dat", "rb") as f:
    l = [0]
    contents = load(f)
    # dump(l, f)
    print(contents)
