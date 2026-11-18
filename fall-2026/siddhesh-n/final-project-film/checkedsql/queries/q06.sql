-- Q06 channel with the highest ROAS (total revenue / total spend per channel)
SELECT channel FROM campaigns GROUP BY channel ORDER BY 1.0 * SUM(revenue) / SUM(spend) DESC LIMIT 1;
