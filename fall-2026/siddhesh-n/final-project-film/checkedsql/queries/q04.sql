-- Q04 overall CTR in percent
SELECT ROUND(100.0 * SUM(clicks) / SUM(impressions), 2) FROM campaigns;
