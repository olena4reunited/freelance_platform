from typing import Any

from psycopg2.extras import RealDictCursor

from server.app.models._base_model import BaseModel
from server.app.database.database import PostgresDatabase


class Team(BaseModel):
    table_name = "teams"

    @staticmethod
    def get_order_team(team_id: int) -> dict[str, Any]:
        with PostgresDatabase() as db:
            with db.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                        SELECT name, lead_id
                        FROM teams
                        WHERE id = %s
                    """,
                    (team_id, )
                )
                team = cursor.fetchone()

                cursor.execute(
                    """
                        SELECT 
                            username,
                            first_name,
                            last_name,
                            photo_link
                        FROM users
                        WHERE id = %s;
                    """,
                    (team["lead_id"], )
                )
                lead = cursor.fetchone()

                cursor.execute(
                    """
                        SELECT 
                            username,
                            first_name,
                            last_name,
                            photo_link
                        FROM users u
                        JOIN teams_users tu
                            ON tu.user_id = u.id
                        WHERE tu.team_id = %s;
                    """,
                    (team_id, )
                )
                team_users = cursor.fetchall()

        team.pop("lead_id")
        team["lead"] = lead
        team["performers"] = team_users
        
        return team
