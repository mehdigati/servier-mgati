SELECT
    date AS date,
    SUM(prod_price * prod_qty) AS ventes
FROM
    `PROJECT_ID.DATASET_NAME.TRANSACTIONS`
WHERE
    date BETWEEN "2019-01-01" AND "2019-12-31"
GROUP BY
    date
ORDER BY
    date ASC
