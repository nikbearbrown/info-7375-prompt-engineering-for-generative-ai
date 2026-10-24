-- DELIBERATELY WRONG version of Q06, kept to prove the checker catches the ratio trap.
-- It averages each row's ROAS instead of dividing total revenue by total spend.
SELECT channel FROM campaigns GROUP BY channel ORDER BY AVG(1.0 * revenue / spend) DESC LIMIT 1;
