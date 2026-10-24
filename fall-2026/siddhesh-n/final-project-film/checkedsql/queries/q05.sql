-- Q05 channel with the most conversions
SELECT channel FROM campaigns GROUP BY channel ORDER BY SUM(conversions) DESC LIMIT 1;
