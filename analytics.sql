-- Number of reports by severity
SELECT final_severity, COUNT(*) AS number_of_reports
FROM production_reports
GROUP BY final_severity;


-- Total downtime by machine
SELECT
    machine_id,
    SUM(downtime_minutes) AS total_downtime
FROM production_reports
GROUP BY machine_id
ORDER BY total_downtime DESC;


SELECT
    machine_id,
    COUNT(*) AS total_reports,

    SUM(
        CASE
            WHEN final_severity = 'HIGH' THEN 1
            ELSE 0
        END
    ) AS high_reports,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN final_severity = 'HIGH' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        1
    ) AS high_percentage

FROM production_reports

GROUP BY machine_id

ORDER BY high_percentage DESC;