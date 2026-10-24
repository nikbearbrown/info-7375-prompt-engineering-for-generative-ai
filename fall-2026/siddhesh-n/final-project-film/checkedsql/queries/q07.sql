-- Q07 Email ROAS
SELECT ROUND(1.0 * SUM(revenue) / SUM(spend), 2) FROM campaigns WHERE channel = 'Email';
