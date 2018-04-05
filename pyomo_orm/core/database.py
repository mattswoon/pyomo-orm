from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker())

def bind_engine(engine_url='sqlite://'):
    engine = create_engine(engine_url)
    Session.configure(bind=engine)
    return engine
