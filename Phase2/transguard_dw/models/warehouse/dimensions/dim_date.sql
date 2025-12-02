SELECT
    date::date AS date_key,
    EXTRACT(day FROM date) AS day,
    EXTRACT(month FROM date) AS month,
    EXTRACT(year FROM date) AS year,
    TO_CHAR(date, 'Month') AS month_name,
    EXTRACT(quarter FROM date) AS quarter
FROM (
    SELECT DISTINCT date::date AS date
    FROM {{ ref('stg_transactions') }}
) d
