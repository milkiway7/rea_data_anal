from sqlalchemy.future import select
from Database.database import Database
from Database.TableModel.ScrappingDataTableModel import scrapped_data_table
from Database.TableModel.ScrappingDataArchiveTableModel import ScrappedDataArchive
from Helpers.logger import get_logger
from Database.Mappers.ScrappedDataMapper import ScrappedDataMapper
from sqlalchemy import text, select, update, delete, func
import asyncio

class ScrappedDataRepository(): 
    def __init__(self):
        self.database = Database()
        self.logger = get_logger(self.__class__.__name__)

    async def save_data(self, data):
        async with self.database.get_session() as session:
            try:
                data_urls = [item["url"] for item in data]
                existing_urls = (
                    await session.execute(select(scrapped_data_table.Url).where(scrapped_data_table.Url.in_(data_urls)))
                ).scalars().all()
                filtered_data = [item for item in data if item["url"] not in existing_urls]

                records = [ScrappedDataMapper.map_to_db_model(item) for item in filtered_data]
                session.add_all(records)
                await session.commit()
                return {"msg": "ok", "inserted": len(records), "dupicates": len(existing_urls)}
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error saving data: {e}")

    async def clear_scrapped_data_and_archive(self, batch_size: int = 5000, sleep_ms: int = 50):
        self.logger.info(f"Archiving data in batches of {batch_size} with sleep {sleep_ms}ms")
        total = 0
        sql = text("""
        WITH to_del AS (
        SELECT TOP (:batch) *
        FROM dbo.ScrappedData WITH (READPAST, ROWLOCK)
        ORDER BY Id
        )
        DELETE FROM to_del
        OUTPUT
        DELETED.CreatedAt,
        DELETED.Url,
        DELETED.Title,
        DELETED.Address,
        DELETED.Price,
        DELETED.PricePerM2,
        DELETED.Description,
        DELETED.Area,
        DELETED.Rooms,
        DELETED.Heating,
        DELETED.Floor,
        DELETED.Rent,
        DELETED.BuildingCondition,
        DELETED.Market,
        DELETED.AvailableFrom,
        DELETED.OfferType,
        DELETED.AdditionalInfo
        INTO dbo.ScrappedDataArchive (
        CreatedAt, Url, Title, Address, Price, PricePerM2, Description, Area,
        Rooms, Heating, Floor, Rent, BuildingCondition, Market, AvailableFrom, OfferType, AdditionalInfo
        );
        """)

        async with self.database.get_session() as s:
            while True:
                async with s.begin():
                    res = await s.execute(sql, {"batch": batch_size})
                affected = res.rowcount or 0  
                total += affected
                if affected < batch_size:
                    self.logger.info(f"Total records archived: {total}")
                    break
                if sleep_ms:
                    self.logger.info(f"Sleeping for {sleep_ms} ms")
                    await asyncio.sleep(sleep_ms / 1000.0)

    async def purge_archive_duplicates_by_url_batched(self, batch_size: int = 5000) -> dict:
        total = 0
        async with self.database.get_session() as session:
            try:
                offset = 0
                while True:
                    urls = (
                        await session.execute(
                            select(scrapped_data_table.Url)
                            .order_by(scrapped_data_table.Id)
                            .offset(offset)
                            .limit(batch_size)
                        )
                    ).scalars().all()

                    if not urls:
                        break

                    async with session.begin():
                        del_stmt = delete(ScrappedDataArchive).where(
                            ScrappedDataArchive.Url.in_(urls)
                        )
                        res = await session.execute(del_stmt)

                    total += res.rowcount or 0
                    offset += batch_size

                self.logger.info(f"Removed {total} archive duplicates by Url (batched).")
                return {"msg": "ok", "deleted": total}
            except Exception as e:
                self.logger.error(f"Error (batched) purging duplicates: {e}")
                return {"msg": "error", "error": str(e)}

    async def mark_soldout_for_nulls_scrapped_archive(self, batch_size: int = 10_000, sleep_ms: int = 25) -> dict:
        total = 0
        async with self.database.get_session() as session:
            try:
                last_id = 0  
                while True:
                    ids = (
                        await session.execute(
                            select(ScrappedDataArchive.Id)
                            .where(ScrappedDataArchive.SoldOut.is_(None))
                            .where(ScrappedDataArchive.Id > last_id)
                            .order_by(ScrappedDataArchive.Id)
                            .limit(batch_size)
                        )
                    ).scalars().all()

                    if not ids:
                        break

                    async with session.begin():
                        res = await session.execute(
                            update(ScrappedDataArchive)
                            .where(ScrappedDataArchive.Id.in_(ids))
                            .values(SoldOut=func.now())  
                        )

                    total += res.rowcount or 0
                    last_id = ids[-1]
                    if sleep_ms:
                        import asyncio
                        await asyncio.sleep(sleep_ms / 1000.0)

                self.logger.info(f"mark_soldout_for_nulls_batched_portable: updated={total}")
                return {"msg": "ok", "updated": total}
            except Exception as e:
                self.logger.error(f"Error in mark_soldout_for_nulls_batched_portable: {e}")
                return {"msg": "error", "error": str(e)}



            