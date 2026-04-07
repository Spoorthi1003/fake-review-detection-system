import pandas as pd

# Load dataset
df = pd.read_csv("Reviews.csv")

# Convert review_date to proper units
df['review_date'] = pd.to_datetime(df['review_date'], unit='s')

# Remove line breaks from review
df['review_text'] = df['review_text'].str.replace('\n',' ', regex=True)

# Limit dataset size
df = df.head(100000)

df.to_csv('clean_reviews.csv', index=False, encoding='utf-8', sep='\t')
