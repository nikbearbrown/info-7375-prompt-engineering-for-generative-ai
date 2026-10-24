-- Q08 Mobile conversion rate in percent (conversions / clicks)
SELECT ROUND(100.0 * SUM(conversions) / SUM(clicks), 2) FROM campaigns WHERE device = 'Mobile';
