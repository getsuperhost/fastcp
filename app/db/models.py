import uuid
from sqlmodel import SQLModel, Field


class Website(SQLModel, table=True):
    __tablename__ = 'websites'

    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    system_user_id: int = Field(
        title='System User ID',
        description='The ID of the system user. For example, the ID of root user is 0.',
        index=True,
    )
    label: str = Field(max_length=255)
    php_version: str = Field(max_length=10)
