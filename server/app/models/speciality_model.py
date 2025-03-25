from server.app.models._base_model import BaseModel
from server.app.database.database import PostgresDatabase


class Speciality(BaseModel):
    table_name = "specialities"

    @staticmethod
    def get_users_specialities_array(user_id: int) -> dict[str, list[str]]:
        with PostgresDatabase() as db:
            return db.fetch(
                """
                    SELECT ARRAY_AGG(sp.name) AS specialities
                    FROM users_specialities usp
                    JOIN specialities sp
                        ON usp.speciality_id = sp.id
                    WHERE usp.user_id = %s 
                """,
                (user_id, )
            )
