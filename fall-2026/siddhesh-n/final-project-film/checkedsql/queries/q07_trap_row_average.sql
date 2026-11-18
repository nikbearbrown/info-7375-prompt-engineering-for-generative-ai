-- DELIBERATELY WRONG version of Q07: row-averaged ROAS for Email.
SELECT ROUND(AVG(1.0 * revenue / spend), 2) FROM campaigns WHERE channel = 'Email';
