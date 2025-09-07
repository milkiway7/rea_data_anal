from Helpers.logger import get_logger
from Database.database import Database
from sqlalchemy.future import select
from sqlalchemy import text
from datetime import datetime, timedelta

class ChartsRepository:
    def __init__(self):
        self.database = Database()
        self.logger = get_logger(self.__class__.__name__)

    async def get_median_price_per_m2(self):
        async with self.database.get_session() as session:
            try:
                self.logger.info("Fetching median price per m2")
                query = text("""
                    WITH base AS (
                        SELECT CAST(CreatedAt AS date) AS d,
                        PricePerM2
                        FROM [RealEstateAgent].[dbo].[ScrappedData]
                        WHERE PricePerM2 > 0
                        ),
                             agg AS(
                                SELECT d, 
                                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY PricePerM2) 
                                OVER (PARTITION BY d) AS med,
                                COUNT(*) OVER (PARTITION BY d) AS n
                                FROM base)
                        SELECT DISTINCT 
                            d AS [date], 
                            med AS median_price_per_m2, 
                            n AS listings_count
                            FROM agg
                            ORDER BY [date];
                """)
                response = await session.execute(query)
                result = [dict(row._mapping) for row in response.fetchall()]
                self.logger.info("Median price per m2 fetched successfully")
                return result
            except Exception as e:
                self.logger.error(f"Error fetching median price per m2: {e}")
                raise

    async def get_price_distribution_per_m2(self):
        async with self.database.get_session() as session:
            try:
                self.logger.info("Fetching price distrpbtion per m2")
                query = text("""
                     WITH q AS (
                        SELECT 
                            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY PricePerM2) OVER () AS q1,
                            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY PricePerM2) OVER () AS q3
                        FROM RealEstateAgent.dbo.ScrappedData
                        WHERE PricePerM2 > 0
                        ),
                        limits AS (
                        SELECT TOP 1 
                                q1, q3, 
                                (q3 - q1) AS iqr 
                        FROM q
                        ),
                        filtered AS (
                        SELECT s.PricePerM2
                        FROM RealEstateAgent.dbo.ScrappedData s
                        CROSS JOIN limits l
                        WHERE PricePerM2 BETWEEN (l.q1 - 1.5 * l.iqr) AND (l.q3 + 1.5 * l.iqr)
                        )
                        SELECT FLOOR(PricePerM2 / 1000.0) * 1000 AS price_m2,
                            COUNT(*) AS offers_count
                        FROM filtered
                        GROUP BY FLOOR(PricePerM2 / 1000.0) * 1000
                        ORDER BY price_m2;
                             """)
                response = await session.execute(query)
                result = [dict((row._mapping)) for row in response.fetchall()]
                self.logger.info("Price distribution per m2 fetched successfully")
                return result
            except Exception as e:
                self.logger.error(f"Error fetching price distribution per m2: {e}")
                raise
    
    async def get_area_dependency_on_price_per_m2(self, start_date: datetime|None=None, end_date: datetime|None=None,sample_modulo:int=10, top_n:int=500):
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(60)

        sql = text("""
        WITH q AS (
        SELECT 
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY PricePerM2) OVER () AS q1,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY PricePerM2) OVER () AS q3
        FROM RealEstateAgent.dbo.ScrappedData
        WHERE PricePerM2 > 0
            AND CreatedAt >= :start_date AND CreatedAt < :end_date
        ),
        limits AS (
        SELECT TOP 1 q1, q3, (q3 - q1) AS iqr FROM q
        ),
        filtered AS (
        SELECT s.Id, s.Price, s.Area, s.Rooms, s.PricePerM2, s.CreatedAt
        FROM RealEstateAgent.dbo.ScrappedData s
        CROSS JOIN limits l
        WHERE s.Price > 0 AND s.Area > 0
            AND s.PricePerM2 BETWEEN (l.q1 - 1.5*l.iqr) AND (l.q3 + 1.5*l.iqr)
            AND s.Area BETWEEN 15 AND 150
            AND s.CreatedAt >= :start_date AND s.CreatedAt < :end_date
        )
        SELECT TOP (:top_n)
        Price, Area, Rooms, PricePerM2, CreatedAt
        FROM filtered
        WHERE ABS(CHECKSUM(Id)) % :sample_modulo = 0
        ORDER BY CreatedAt DESC;
        """)
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "sample_modulo": sample_modulo,
            "top_n": top_n,
        }
        async with self.database.get_session() as session:
            res = await session.execute(sql, params)
            rows = [dict(r._mapping) for r in res.fetchall()]
            # opcjonalnie: normalizacja kluczy pod frontend
            for r in rows:
                r["price"] = r.pop("Price")
                r["area"] = r.pop("Area")
                r["rooms"] = r.pop("Rooms")
                r["pricePerM2"] = r.pop("PricePerM2")
                r["createdAt"] = r.pop("CreatedAt")
            return rows