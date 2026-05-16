import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import seaborn as sns

conn = mysql.connector.connect (
    host = "localhost" ,
    user = "root",
    password = "root123",
    database = "fake_review_detector"
)

# Load user scores 
userscore_df = pd.read_sql(""" 
                 SELECT * FROM scoring_users
                 """ , conn)

print(userscore_df.head())

# Load reviews
review_df = pd.read_sql(""" 
                        SELECT * FROM reviews
                        """, conn)

print(review_df.head())

fraud_counts = userscore_df['fraud_score'].value_counts().sort_index()

# Plot user score Vs number of people
fraud_counts.plot(kind="bar")
plt.title("Fraud score distribution")
plt.xlabel("Suspicious users (on scale of 0 to 3)")
plt.ylabel("Number of people")
plt.yscale('log')
plt.savefig("fraud_score.png")
plt.show()

# Most affected products
affected_products = pd.read_sql("""
    WITH suspicious_reviews AS(
SELECT r.product_id, COUNT(*) AS suspicious_review_cnt
FROM reviews r JOIN
scoring_users s 
ON s.user_id = r.user_id
WHERE s.fraud_score >= 2
GROUP BY r.product_id
),
rankings AS (
SELECT * , DENSE_RANK() OVER 
(ORDER BY suspicious_review_cnt DESC) AS ranks
FROM suspicious_reviews)
SELECT product_id, suspicious_review_cnt
FROM rankings
WHERE ranks <=5
ORDER BY suspicious_review_cnt DESC """, conn)

sns.barplot(data=affected_products, x="suspicious_review_cnt", y="product_id")
plt.title("Most affected products")
plt.tight_layout()
# plt.savefig("affected_products.png")
plt.show()

# % suspicious reviews on products
percentage_df = pd.read_sql(""" WITH total_reviews AS (
SELECT product_id, COUNT(*) AS total
FROM reviews
GROUP BY product_id
),
suspicious_reviews AS (
SELECT r.product_id, t.total, 
COUNT(*) AS suspicious_review_cnt,
ROUND(COUNT(*)*100.0/t.total,1)
AS percent_suspicious_reviews
FROM reviews r JOIN total_reviews t
ON r.product_id = t.product_id 
JOIN scoring_users s 
ON r.user_id = s.user_id
WHERE s.fraud_score >=2 AND t.total > 20
GROUP BY r.product_id, t.total
), 
ranking AS (
SELECT * , DENSE_RANK() OVER 
(ORDER BY percent_suspicious_reviews DESC) AS ranks
FROM suspicious_reviews
)
SELECT product_id, total , suspicious_review_cnt,
percent_suspicious_reviews
FROM ranking
WHERE ranks <= 5
ORDER BY percent_suspicious_reviews DESC""", conn)

percentage_df = percentage_df.sort_values(by="percent_suspicious_reviews", ascending=False)

sns.barplot(data=percentage_df, x="percent_suspicious_reviews", y="product_id", errorbar=None)
plt.title("Top Products by % Suspicious Reviews")
plt.tight_layout()
plt.savefig("percentage_suspicious_reviews.png")
plt.show()

# Rating distribution
rating_df = pd.read_sql(""" SELECT s.fraud_score , r.rating,
COUNT(*) AS review_count
FROM scoring_users s JOIN
reviews r
ON r.user_id = s.user_id
WHERE r.rating IN (1,5)
GROUP BY s.fraud_score, r.rating
ORDER BY s.fraud_score DESC
                    """, conn)

pivot_df = rating_df.pivot(index='fraud_score', columns='rating', values='review_count')
pivot_df.plot(kind="bar", stacked=True)
plt.title("Extreme Rating Behavior Among Users by Fraud Score")
plt.ylabel("Number of people")
plt.yscale('log')
plt.savefig("rating_distribution.png")
plt.show()

# Spike detection
burst_df = pd.read_sql("""
SELECT 
    product_id,
    DATE(review_date) AS review_day,
    COUNT(*) AS reviews_per_day
FROM reviews
GROUP BY product_id, DATE(review_date)
HAVING COUNT(*) > 20
ORDER BY reviews_per_day DESC
LIMIT 1
""", conn)

product = burst_df['product_id'][0]

trend_df = pd.read_sql(f"""
SELECT 
    DATE(review_date) AS review_day,
    COUNT(*) AS reviews_per_day
FROM reviews
WHERE product_id = '{product}'
GROUP BY DATE(review_date)
ORDER BY review_day
""", conn)

plt.plot(trend_df['review_day'], trend_df['reviews_per_day'])
plt.title(f"Review Trend for Product {product}")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("spike_detection.png")
plt.show()

with pd.ExcelWriter('review_fraud_detection.xlsx') as writer:
    userscore_df.to_excel(writer, sheet_name="user_scores", index=False)
    affected_products.to_excel(writer, sheet_name="affected_products", index=False)
    percentage_df.to_excel(writer, sheet_name="percentage_suspicious_reviews", index=False)
    rating_df.to_excel(writer, sheet_name="rating_distribution", index=False)
    trend_df.to_excel(writer, sheet_name="review_trend", index=False)
