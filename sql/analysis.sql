-- Users rating more than 20 products
SELECT user_id , COUNT(*) AS review_count
FROM reviews
GROUP BY user_id
HAVING review_count>20
ORDER BY review_count DESC;

-- Users writing multiple reviews on a single day
SELECT user_id , review_date, COUNT(*)
AS review_per_day
FROM reviews
GROUP BY user_id, review_date
HAVING review_per_day > 7
ORDER BY review_per_day DESC;

-- Extreme rating behavior
SELECT user_id , AVG(rating) AS average_rating ,
COUNT(*) AS review_count
FROM reviews
GROUP BY user_id
HAVING average_rating IN (1,5)
AND review_count > 5
ORDER BY review_count DESC;

-- Creating fraud_users view
CREATE VIEW fraud_users_view AS 
WITH user_stats AS(
SELECT user_id , AVG(rating) AS average_rating,
COUNT(*) AS review_count
FROM reviews
GROUP BY user_id 
HAVING average_rating IN (1,5) AND 
review_count > 5
), 
daily_spam AS (
SELECT user_id, MAX(review_per_day) AS max_review_per_day
FROM (
SELECT user_id, review_date , 
COUNT(*) AS review_per_day
FROM reviews
GROUP BY user_id, review_date
HAVING review_per_day > 7 ) t
GROUP BY user_id
),
fraud_users AS (
SELECT u.user_id, u.average_rating,
d.max_review_per_day ,
(CASE WHEN u.average_rating IN (1,5) THEN 1 ELSE 0 END +
CASE WHEN u.review_count > 20 THEN 1 ELSE 0 END +
CASE WHEN d.max_review_per_day > 7 THEN 1 ELSE 0 END)
AS fraud_score
FROM user_stats u JOIN
daily_spam d ON
u.user_id = d.user_id 
ORDER BY fraud_score DESC)
SELECT * FROM fraud_users;

-- Check view
SELECT * FROM fraud_users_view;

 -- Most affected products
SELECT r.product_id , COUNT(*) AS suspicious_reviews
FROM fraud_users_view f
JOIN reviews r
ON r.user_id = f.user_id
WHERE f.fraud_score >=2 
GROUP BY r.product_id
ORDER BY suspicious_reviews DESC
LIMIT 10;

-- Percentage of suspicious reviews for most suspicious products
WITH total_reviews AS (
SELECT product_id, COUNT(*) AS total
FROM reviews
GROUP BY product_id
)
SELECT r.product_id, COUNT(*) AS suspicious_reviews,
t.total, CONCAT(ROUND(COUNT(*)*100/t.total,2),'%')
AS percent_suspicious_reviews
FROM reviews r
JOIN total_reviews t
ON t.product_id = r.product_id
JOIN fraud_users_view f
ON f.user_id = r.user_id
WHERE f.fraud_score >=2 AND t.total >= 20
GROUP BY r.product_id 
ORDER BY ROUND(COUNT(*)*100/t.total,2) DESC;

-- Text duplication
SELECT review_text , COUNT(*) AS occurance
FROM reviews
GROUP BY review_text
HAVING occurance > 5
ORDER BY occurance DESC;

-- Products with large reviews per day
SELECT product_id, review_date, 
COUNT(*) AS review_per_day
FROM reviews
GROUP BY product_id, review_date
HAVING COUNT(*) > 20
ORDER BY review_per_day DESC;

-- Distribution of ratings
SELECT f.fraud_score , r.rating,
COUNT(*) AS review_count
FROM fraud_users_view f JOIN
reviews r
ON r.user_id = f.user_id
WHERE f.fraud_score >= 2
GROUP BY f.fraud_score, r.rating
ORDER BY COUNT(*) DESC;

-- Time gap between first and last review
SELECT user_id , MIN(review_date) AS first_active,
MAX(review_date) AS last_active,
TIMESTAMPDIFF(DAY, MIN(review_date) , MAX(review_date)) AS active_days,
COUNT(*) AS total_reviews
FROM reviews
GROUP BY user_id
HAVING total_reviews > 20 AND active_days <= 100
ORDER BY active_days;
