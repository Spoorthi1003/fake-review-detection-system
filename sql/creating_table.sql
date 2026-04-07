-- Create database
CREATE DATABASE fake_review_detector;
USE fake_review_detector;

-- Create reviews table
CREATE TABLE reviews(
review_id INT ,
product_id VARCHAR(50),
user_id VARCHAR(50),
rating INT,
review_date DATE,
review_text LONGTEXT
);

SET GLOBAL local_infile = 1;

-- Import csv file into SQL
LOAD DATA LOCAL INFILE 'C:/Users/sua5/Desktop/CWH/fake-review-detector/clean_reviews.csv'
INTO TABLE reviews
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Check number of rows
SELECT COUNT(*) FROM reviews;
