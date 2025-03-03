from typing import Any

from psycopg2 import sql
from psycopg2.extras import RealDictCursor

from server.app.models._base_model import BaseModel
from server.app.database.database import PostgresDatabase


class UserProfileFeedback(BaseModel):
    table_name = "users_profile_feedbacks"

    @staticmethod
    def create_feedback(
            user_id: int,
            commentator_id: int,
            feedback: dict[str, Any]
    ) -> dict[str, Any] | None:
        with PostgresDatabase(on_commit=True) as db:
            return db.fetch(
                """
                    WITH inserted_feedback AS (
                        INSERT INTO users_profile_feedbacks 
                            (content,
                             rate,
                             commentator_id,
                             profile_id)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, content, rate, commentator_id, profile_id
                    ),
                    inserted_image AS (
                        INSERT INTO profile_feedbacks_images 
                            (image_link, profile_feedback_id)
                        SELECT %s, inf.id
                        FROM inserted_feedback inf
                        WHERE %s IS NOT NULL
                        ON CONFLICT DO NOTHING
                        RETURNING id, image_link, profile_feedback_id
                    )
                    SELECT 
                        if.id AS id,
                        content, 
                        rate, 
                        commentator_id, 
                        profile_id, 
                        ini.image_link AS image_link
                    FROM inserted_feedback if
                    LEFT JOIN inserted_image ini 
                        ON ini.profile_feedback_id = if.id;
                """,
                (
                    feedback["content"],
                    feedback["rate"],
                    commentator_id,
                    user_id,
                    feedback["image_link"],
                    feedback["image_link"]
                ),
            )

    @staticmethod
    def get_all_user_feedback(user_id: int) -> list[dict[str, Any]] | dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_user_feedback AS (
                        SELECT 
                            id, 
                            content, 
                            rate,
                            commentator_id,
                            profile_id
                        FROM users_profile_feedbacks
                        WHERE profile_id = %s
                    ),
                    selected_feedback_images AS (
                        SELECT image_link, profile_feedback_id
                        FROM selected_user_feedback suf
                        JOIN profile_feedbacks_images pfi 
                            ON pfi.profile_feedback_id = suf.id
                    )
                    SELECT 
                        id, 
                        content, 
                        rate, 
                        commentator_id, 
                        profile_id, 
                        image_link
                    FROM selected_user_feedback suf
                    LEFT JOIN selected_feedback_images sfi
                        ON suf.id = sfi.profile_feedback_id
                """,
                (user_id,),
                is_all=True
            )

    @staticmethod
    def get_user_feedback(feedback_id: int) -> dict[str, Any] | None:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    WITH selected_user_feedback AS (
                        SELECT 
                            id, 
                            content, 
                            rate,
                            commentator_id,
                            profile_id
                        FROM users_profile_feedbacks
                        WHERE id = %s
                    ),
                    selected_feedback_images AS (
                        SELECT image_link, profile_feedback_id
                        FROM profile_feedbacks_images 
                        WHERE profile_feedback_id = %s
                    )
                    SELECT 
                        id, 
                        content, 
                        rate, 
                        commentator_id, 
                        profile_id, 
                        image_link
                    FROM selected_user_feedback suf
                    LEFT JOIN selected_feedback_images sfi
                        ON suf.id = sfi.profile_feedback_id
                """,
                (feedback_id, feedback_id, ),
            )

    @staticmethod
    def update_user_profile_feedback(feedback_id: int, feedback: dict[str, Any]) -> dict[str, Any] | None:
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder())
            for k in feedback.keys() if k != "image_link" and feedback[k] is not None
        )
        params = tuple(v for k, v in feedback.items() if k != "image_link" and v is not None) + (feedback_id,)

        query = sql.SQL("""
            WITH updated_feedback AS (
                UPDATE users_profile_feedbacks 
                SET {set_clause}
                WHERE id = %s
                RETURNING id
            )
            UPDATE profile_feedbacks_images
            SET image_link = COALESCE(%s, image_link)
            WHERE profile_feedback_id = (SELECT id FROM updated_feedback)
        """).format(set_clause=set_clause)

        with PostgresDatabase(on_commit=True) as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    query,
                    params + (feedback.get("image_link", None),),
                )

                cursor.execute(
                    sql.SQL("""
                        WITH selected_user_feedback AS (
                        SELECT 
                            id, 
                            content, 
                            rate,
                            commentator_id,
                            profile_id
                        FROM users_profile_feedbacks
                        WHERE id = %s
                        ),
                        selected_feedback_images AS (
                            SELECT image_link, profile_feedback_id
                            FROM profile_feedbacks_images 
                            WHERE profile_feedback_id = %s
                        )
                        SELECT 
                            id, 
                            content, 
                            rate, 
                            commentator_id, 
                            profile_id, 
                            image_link
                        FROM selected_user_feedback suf
                        LEFT JOIN selected_feedback_images sfi
                            ON suf.id = sfi.profile_feedback_id
                    """),
                    (feedback_id, feedback_id, ),
                )
                return cursor.fetchone()
