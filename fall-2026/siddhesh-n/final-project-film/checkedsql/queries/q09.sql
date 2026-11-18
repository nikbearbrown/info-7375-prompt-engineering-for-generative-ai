-- Q09 week with the highest profit
SELECT week FROM campaigns GROUP BY week ORDER BY SUM(revenue) - SUM(spend) DESC LIMIT 1;
