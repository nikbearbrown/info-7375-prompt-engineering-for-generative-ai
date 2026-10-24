-- Q03 overall ROAS = total revenue / total spend
SELECT ROUND(1.0 * SUM(revenue) / SUM(spend), 2) FROM campaigns;
