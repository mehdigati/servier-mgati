SELECT
    t.client_id AS client_id,
    SUM(
        CASE
            WHEN pn.product_type = 'MEUBLE' THEN t.prod_price * t.prod_qty
            ELSE 0
        END
    ) AS ventes_meuble,
    SUM(
        CASE
            WHEN pn.product_type = 'DECO' THEN t.prod_price * t.prod_qty
            ELSE 0
        END
    ) AS ventes_deco
FROM
    `PROJECT_ID.DATASET_NAME.TRANSACTIONS` AS t
LEFT JOIN `PROJECT_ID.DATASET_NAME.PRODUCT_NOMENCLATURE` AS pn ON t.prod_id = pn.product_id
WHERE
    t.date BETWEEN "2019-01-01" AND "2019-12-31"
GROUP BY
    client_id
