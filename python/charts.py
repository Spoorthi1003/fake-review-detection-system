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

# Load suspicious users
suspicious_df = pd.read_sql(""" 
                 SELECT * FROM fraud_users_view
                 """ , conn)

print(suspicious_df.head())

# Load reviews
review_df = pd.read_sql(""" 
                        SELECT * FROM reviews
                        """, conn)

print(review_df.head())

fraud_counts = suspicious_df['fraud_score'].value_counts().sort_index()

fraud_counts = fraud_counts.reindex([0,1,2,3], fill_value=0)

# Plot suspicious user score Vs number of people
fraud_counts.plot(kind="bar")
plt.title("Fraud score distribution")
plt.xlabel("Suspicious users (on scale of 0 to 3)")
plt.ylabel("Number of people")
plt.savefig("fraud_score.png")
plt.show()

# Most affected products
affected_products = pd.read_sql("""
    SELECT r.product_id, COUNT(*) AS 
    suspicious_reviews FROM reviews r
    JOIN fraud_users_view f
    ON r.user_id = f.user_id
    WHERE f.fraud_score >=2
    GROUP BY r.product_id
    ORDER BY COUNT(*) DESC
    LIMIT 10""", conn)

sns.barplot(data=affected_products, x="suspicious_reviews", y="product_id")
plt.title("Affected products")
plt.tight_layout()
plt.savefig("affected_products.png")
plt.show()

# % suspicious reviews on products
percentage_df = pd.read_sql(""" WITH total_reviews AS (
SELECT product_id, COUNT(*) AS total
FROM reviews
GROUP BY product_id
)
SELECT r.product_id, COUNT(*) AS suspicious_reviews,
t.total, ROUND(COUNT(*)*100/t.total,2)
AS percent_suspicious_reviews
FROM reviews r
JOIN total_reviews t
ON t.product_id = r.product_id
JOIN fraud_users_view f
ON f.user_id = r.user_id
WHERE f.fraud_score >=2 AND t.total >= 20
GROUP BY r.product_id 
ORDER BY ROUND(COUNT(*)*100/t.total,2) DESC
LIMIT 10""", conn)

percentage_df['percent_suspicious_reviews'] = percentage_df['percent_suspicious_reviews'].astype(float)

percentage_df = percentage_df.sort_values(by="percent_suspicious_reviews", ascending=False)

sns.barplot(data=percentage_df, x="percent_suspicious_reviews", y="product_id", errorbar=None)
plt.title("Top Products by % Suspicious Reviews")
plt.tight_layout()
plt.savefig("percentage_suspicious_reviews.png")
plt.show()

# Rating distribution
rating_df = pd.read_sql(""" SELECT f.fraud_score,
    r.rating, COUNT(*) AS review_count
    FROM reviews r JOIN fraud_users_view f
    ON r.user_id = f.user_id
    GROUP BY f.fraud_score, r.rating
                    """, conn)

pivot_df = rating_df.pivot(index='fraud_score', columns='rating', values='review_count')
pivot_df.plot(kind="bar", stacked=True)
plt.title("Rating Distribution by Fraud Score")
plt.ylabel("Count")
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

# Export data to excel
with pd.ExcelWriter('review_fraud_detection.xlsx') as writer:
    suspicious_df.to_excel(writer, sheet_name="suspicious_users", index=False)
    affected_products.to_excel(writer, sheet_name="affected_products", index=False)
    percentage_df.to_excel(writer, sheet_name="percentage_suspicious_reviews", index=False)
    rating_df.to_excel(writer, sheet_name="rating_distribution", index=False)
    trend_df.to_excel(writer, sheet_name="review_trend", index=False)
