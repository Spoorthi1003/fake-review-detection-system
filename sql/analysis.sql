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

-- Creating scoring_users view
CREATE VIEW scoring_users AS 
WITH user_stats AS(
SELECT user_id , AVG(rating) AS average_rating,
COUNT(*) AS review_count
FROM reviews
GROUP BY user_id 
), 
daily_spam AS (
SELECT user_id, MAX(review_per_day) AS max_review_per_day
FROM (
SELECT user_id, review_date , 
COUNT(*) AS review_per_day
FROM reviews
GROUP BY user_id, review_date ) t
GROUP BY user_id
),
score AS (
SELECT u.user_id, u.average_rating,
COALESCE(d.max_review_per_day,0) AS max_review_per_day ,
(CASE WHEN u.average_rating <= 1.5 OR u.average_rating >= 4.5
 THEN 1 ELSE 0 END +
CASE WHEN u.review_count > 20 THEN 1 ELSE 0 END +
CASE WHEN COALESCE(d.max_review_per_day,0) > 7 THEN 1 ELSE 0 END)
AS fraud_score
FROM user_stats u LEFT JOIN
daily_spam d ON
u.user_id = d.user_id 
ORDER BY fraud_score DESC)
SELECT * FROM score;

-- Check view
SELECT * FROM scoring_users;

 -- Top 5 products with most suspicious reviews
CREATE VIEW top_suspicious_products_view AS
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
ORDER BY suspicious_review_cnt DESC ;

SELECT * FROM top_suspicious_products_view;

-- Top 5 products with highest % suspicious reviews
CREATE VIEW suspicious_review_percentage_view AS
WITH total_reviews AS (
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
ORDER BY percent_suspicious_reviews DESC;

SELECT * FROM suspicious_review_percentage_view;

-- Total suspicious reviews
SELECT COUNT(*) AS suspicious_reviews
FROM reviews r 
JOIN scoring_users s 
ON s.user_id = r.user_id
WHERE s.fraud_score>=2;

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
CREATE VIEW rating_distribution_view AS
SELECT s.fraud_score , r.rating,
COUNT(*) AS review_count
FROM scoring_users s JOIN
reviews r
ON r.user_id = s.user_id
GROUP BY s.fraud_score, r.rating
ORDER BY s.fraud_score DESC;

SELECT * FROM rating_distribution_view;

-- Time gap between first and last review
SELECT user_id , MIN(review_date) AS first_active,
MAX(review_date) AS last_active,
TIMESTAMPDIFF(DAY, MIN(review_date) , MAX(review_date)) AS active_days,
COUNT(*) AS total_reviews
FROM reviews
GROUP BY user_id
HAVING total_reviews > 20 AND active_days <= 100
ORDER BY active_days;

-- View for review spike analysis
CREATE VIEW review_spike_view AS
SELECT 
    product_id,
    DATE(review_date) AS review_day,
    COUNT(*) AS reviews_per_day
FROM reviews
GROUP BY product_id, DATE(review_date)
ORDER BY COUNT(*) DESC;

SELECT * FROM review_spike_view;