SELECT COUNT(*) FROM defaultdb.ah_snapshots;

SELECT item_id, captured_at, min_price 
FROM defaultdb.ah_snapshots 
ORDER BY captured_at;