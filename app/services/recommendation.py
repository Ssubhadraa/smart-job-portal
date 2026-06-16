from sqlalchemy import text

from app import db


RECOMMENDATION_QUERY = """
SELECT
    j.id,
    j.title,
    j.location,
    j.job_type,
    j.experience_min,
    j.salary_min,
    j.salary_max,
    j.posted_at,
    cp.company_name,
    COUNT(js.skill_id) AS required_count,
    COUNT(CASE WHEN ss.skill_id IS NOT NULL THEN 1 END) AS matched_count,
    ROUND(
        COUNT(CASE WHEN ss.skill_id IS NOT NULL THEN 1 END) * 100.0
        / NULLIF(COUNT(js.skill_id), 0), 1
    ) AS match_score
FROM jobs j
JOIN company_profiles cp ON j.company_id = cp.id
JOIN job_skills js ON j.id = js.job_id AND js.is_required = 1
LEFT JOIN student_skills ss
    ON js.skill_id = ss.skill_id AND ss.student_id = :student_id
WHERE j.status = 'active'
GROUP BY j.id
HAVING match_score >= 30
ORDER BY match_score DESC, j.posted_at DESC
LIMIT 20
"""


def get_recommendations(student_id):
    if not student_id:
        return []

    result = db.session.execute(
        text(RECOMMENDATION_QUERY),
        {"student_id": student_id},
    )
    rows = result.mappings().all()
    return [dict(row) for row in rows]


def get_match_score(student_id, job_id):
    query = """
    SELECT
        ROUND(
            COUNT(CASE WHEN ss.skill_id IS NOT NULL THEN 1 END) * 100.0
            / NULLIF(COUNT(js.skill_id), 0), 1
        ) AS match_score
    FROM jobs j
    JOIN job_skills js ON j.id = js.job_id AND js.is_required = 1
    LEFT JOIN student_skills ss
        ON js.skill_id = ss.skill_id AND ss.student_id = :student_id
    WHERE j.id = :job_id
    GROUP BY j.id
    """
    result = db.session.execute(
        text(query),
        {"student_id": student_id, "job_id": job_id},
    ).scalar()
    return float(result) if result is not None else 0.0
