import functools
import logging
import os
from time import time

from pymongo import MongoClient

from .mongodb_handler import MongoDBHandler


class MongoDBLogDecorator:
    """
    MongoDB 로깅 핸들러에 데코레이터 패턴을 적용하여
    추가 기능을 제공하는 클래스입니다.
    """

    def __init__(
        self,
        connection_string: str,
        db_name: str,
        collection_name: str,
    ) -> None:
        # MongoDB 클라이언트 및 컬렉션 초기화
        self.client = MongoClient(host=connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        # 로거 및 핸들러 설정
        self.logger = logging.getLogger(name="MongoDBLogger")
        self.logger.setLevel(level=logging.DEBUG)

        # 중복 핸들러 추가 방지
        if not self.logger.handlers:
            mongo_handler = MongoDBHandler(collection=self.collection)
            self.logger.addHandler(hdlr=mongo_handler)

    def __call__(self, func):

        @functools.wraps(wrapped=func)
        def wrapper(*args, **kwargs):
            start_time = time()
            result = None
            error_msg = None
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result

            except Exception as e:
                status = "error"
                error_msg = str(e)
                raise
            finally:
                duration = (time() - start_time) * 1000  # 밀리초 단위

                log_payload = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "result": str(result),
                    "exception": error_msg,
                    "status": status,
                    "duration_ms": round(number=duration, ndigits=2),
                }

                match status:
                    case "success":
                        self.logger.info(msg=log_payload)
                    case "error":
                        self.logger.error(msg=log_payload)

        return wrapper


# 3. 사용 예시
if __name__ == "__main__":
    # 데코레이터 인스턴스 생성 (DB 정보 설정)
    # 실제 환경에서는 환경변수나 설정 파일에서 로드하세요.
    log_to_mongo = MongoDBLogDecorator(
        connection_string=os.getenv(key="MONGODB_CONNECTION_STRING"),
        db_name="app_logs",
        collection_name="function_traces",
    )
    print("MongoDBLogDecorator 데코레이터 테스트 시작.")

    @log_to_mongo
    def calculate_payment(price, tax_rate):
        if price < 0:
            raise ValueError("가격은 음수일 수 없습니다.")
        return price * (1 + tax_rate)

    # 정상 실행 테스트
    print("Run 1:", calculate_payment(1000, 0.1))

    # 에러 실행 테스트
    try:
        calculate_payment(-100, 0.1)
    except ValueError:
        print("Run 2: 에러가 정상적으로 로깅되었습니다.")
