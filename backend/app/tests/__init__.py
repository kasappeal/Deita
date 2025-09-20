import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import create_access_token
from app.core.database import Base, get_db
from app.main import app
from app.models import User


class APITest:

    TEST_DATABASE_URL = "sqlite:///./test.db"

    def _create_user(self, email: str, full_name: str = 'Test User') -> User:
        """
        Creates and persists a new User instance in the test database.

        Args:
            email (str): The email address of the user to create.
            full_name (str, optional): The full name of the user. Defaults to 'Test User'.

        Returns:
            User: The newly created and persisted User object.
        """
        user = User(email=email, full_name=full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.db.close()
        return user

    def _get_auth_headers(self, user: User) -> dict:
        """
        Generate authentication headers for a given user.

        Args:
            user (User): The user instance for whom to generate the authentication token.

        Returns:
            dict: A dictionary containing the 'Authorization' header with a Bearer token.
        """
        token = create_access_token({"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}

    def _create_workspace_via_api(self, user: User | None = None, name="UploadTest Workspace", visibility="public"):
        resp = self.client.post(
            "/v1/workspaces/",
            json={"name": name, "visibility": visibility},
            headers=self._get_auth_headers(user) if user else None
        )
        assert resp.status_code == 201
        return resp.json()

    def _create_file_via_api(self, workspace_id: str, filename: str, user: User | None = None):
        files = {"file": (filename, b"some,data,to,upload\n1,2,3,4\n5,6,7,8")}
        resp = self.client.post(
            f"/v1/workspaces/{workspace_id}/files",
            files=files,
            headers=self._get_auth_headers(user) if user else None
        )
        assert resp.status_code == 201
        return resp.json()['file']

    @pytest.fixture
    def db_engine(self):
        return create_engine(
            self.TEST_DATABASE_URL, connect_args={"check_same_thread": False}
        )

    @pytest.fixture(scope="function", autouse=True)
    def setup_method(self, db_engine):
        self.client = TestClient(app)
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        self.db = TestSession()
        app.dependency_overrides[get_db] = lambda: self.db
        Base.metadata.create_all(bind=db_engine)
        yield
        Base.metadata.drop_all(bind=db_engine)
        self.db.close()
        # Remove the sqlite file after test
        db_path = self.TEST_DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_path):
            os.remove(db_path)
