import sys
import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Add the project root directory to the path to import modules from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_db():
    """
    Creates the database schema ONCE for the entire test session.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(setup_db):
    """
    Provides a session for each test within a transaction.
    Rolls back after the test, so the database returns to a clean state
    without the need to physically delete tables.
    """
    connection = engine.connect()
    transaction = connection.begin()
    
    session = TestingSessionLocal(bind=connection)
    
    # Begin a nested transaction (SAVEPOINT).
    # This ensures that session.commit() in tests only commits to this savepoint,
    # not the outer transaction.
    session.begin_nested()

    # If the test calls session.commit(), we need to start a new nested transaction
    # so that subsequent operations are also in a savepoint.
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            session.expire_all()
            session.begin_nested()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
