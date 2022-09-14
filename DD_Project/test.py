import pandas as pd

df = pd.DataFrame()

# create multiindex

index = pd.MultiIndex(levels=[[], []], codes=[[], []], names=['ticker', 'filing'])


df = pd.DataFrame(index=index)

df["ticker", "filing"]


# pickle dataframe
with open('test.pickle', 'wb') as f:
    pickle.dump(df, f)