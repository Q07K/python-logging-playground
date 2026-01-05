import logging
from datetime import datetime

from pymongo.collection import Collection


# MongoDB 동기 로깅 핸들러 정의
class MongoDBHandler(logging.Handler):
    """
    Python 표준 로깅 핸들러를 상속받아
    MongoDB에 로그를 저장하는 핸들러입니다.
    """

    def __init__(self, collection: Collection):
        super().__init__()
        self.collection = collection

    def emit(self, record: logging.LogRecord) -> None:
        """LogRecord를 MongoDB 컬렉션에 저장합니다.

        Parameters
        ----------
        record : logging.LogRecord
            저장할 로그 레코드 객체.
        """
        try:
            if isinstance(record.msg, dict):
                log_entry = record.msg
            else:
                log_entry = {"message": str(record.msg)}

            log_entry.update(
                {
                    "timestamp": datetime.now(),
                    "level": record.levelname,
                }
            )
            # MongoDB에 로그 항목 삽입(동기)
            self.collection.insert_one(log_entry)
        except Exception:
            self.handleError(record)
