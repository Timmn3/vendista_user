from sqlalchemy import Column, BigInteger, String, sql, Float, Boolean

from utils.db_api.db_gino import TimedBaseModel


class IndividualEntrepreneur(TimedBaseModel):
    __tablename__ = 'Individual_entrepreneur'
    user_id = Column(BigInteger, primary_key=True)
    tg_first_name = Column(String(250))
    tg_last_name = Column(String(250))
    name = Column(String(100))
    email = Column(String(50))
    password = Column(String(50))
    time_update = Column(BigInteger)
    status = Column(String(25))
    is_run = Column(Boolean)
    balance = Column(Float)
    number_ie = Column(BigInteger)
    sms_status = Column(Boolean)
    bill_id = Column(String(200))

    query: sql.select
