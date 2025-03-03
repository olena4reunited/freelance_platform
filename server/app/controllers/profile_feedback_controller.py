from typing import Any

from server.app.database.database import PostgresDatabase


class ProfileFeedbackController:
    @staticmethod
    def create_feedback(user_id: int, commentator_id: int, feedback: dict[str, Any]) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                    WITH inserted_feedback AS (
                        INSERT INTO users_profile_feedbacks (content, rate, commentator_id, profile_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, content, rate, commentator_id, profile_id
                    ),
                    inserted_image AS (
                        INSERT INTO profile_feedbacks_images (image_link, profile_feedback_id)
                        SELECT %s, inf.id
                        FROM inserted_feedback inf
                        WHERE %s IS NOT NULL
                        ON CONFLICT DO NOTHING
                        RETURNING id, image_link, profile_feedback_id
                    )
                    SELECT if.id AS id, content, rate, commentator_id, profile_id, COALESCE(ini.image_link, NULL) AS image_link
                    FROM inserted_feedback if
                    LEFT JOIN inserted_image ini ON ini.profile_feedback_id = if.id;
                """,
                (feedback["content"], feedback["rate"], commentator_id, user_id, feedback["image_link"], feedback["image_link"]),
            )
