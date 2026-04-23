from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.domain.repositories.data_source import IDataSource
from app.domain.models.value_objects import DatabaseSource


class SQLDataSource(IDataSource):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_allowed_fields(self, table_name: str) -> set[str]:
        """Возвращает список разрешенных полей для запроса"""
        query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table_name             
        """)

        result = await self._session.execute(query, {"table_name": table_name})
        return {row[0] for row in result.fetchall()}

    async def fetch_data(self, source: DatabaseSource) -> list[dict]:
        try:
            if source.fields in await self._get_allowed_fields(source.table):
                fields_str = ", ".join(source.fields)
            else:
                raise ValueError("Fields not allowed")

            query = f"""
            SELECT {fields_str}
            FROM {source.table}
            WHERE {source.date_field} BETWEEN :date_from AND :date_to
            """

            params = {
                "date_from": source.date_from,
                "date_to": source.date_to,
            }

            if source.filters:
                for key, value in source.filters.items():
                    if isinstance(value, dict):
                        for op, val in value.items():
                            if op == "gte":
                                query += f" AND {key} >= :{key}_gte"
                                params[f"{key}_gte"] = val
                            elif op == "lte":
                                query += f" AND {key} <= :{key}_lte"
                                params[f"{key}_lte"] = val
                            elif op == "gt":
                                query += f" AND {key} > :{key}_gt"
                                params[f"{key}_gt"] = val
                            elif op == "lt":
                                query += f" AND {key} < :{key}_lt"
                                params[f"{key}_lt"] = val
                    else:
                        query += f" AND {key} = :{key}"
                        params[key] = value

            result = await self._session.execute(text(query), params)
            rows = result.fetchall()

            return [dict(zip(source.fields, row)) for row in rows]
        except Exception as e:
            raise ValueError(f"Failed to fetch data: {e}")
