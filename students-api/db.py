from datetime import datetime
from os import environ

import sqlalchemy as sqlalchemy
from sqlalchemy.dialects.postgresql import UUID

connect_str =\
    'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'\
    .format(**environ)
engine = sqlalchemy.create_engine(connect_str)

metadata = sqlalchemy.MetaData()
metadata.bind = engine
now = datetime.utcnow
default_now = dict(default=now, server_default=sqlalchemy.func.now())
new_uuid = sqlalchemy.text('uuid_generate_v4()')

print('potaaatoo db')
students = sqlalchemy.Table('students', metadata,
                            sqlalchemy.Column('id', UUID(
                                as_uuid=True), primary_key=True,
                                server_default=new_uuid, nullable=False),
                            sqlalchemy.Column(
                                'name', sqlalchemy.String(), nullable=False),
                            sqlalchemy.Column(
                                'gender', sqlalchemy.String, nullable=False),
                            sqlalchemy.Column(
                                'state', sqlalchemy.String, nullable=False),
                            sqlalchemy.Column(
                                'department', sqlalchemy.String, nullable=False),
                            sqlalchemy.Column(
                                'date_of_birth', sqlalchemy.Date,
                                nullable=False),
                            sqlalchemy.Column(
                                'created_at', sqlalchemy.DateTime,
                                nullable=False, **default_now),
                            sqlalchemy.Column(
                                'updated_at', sqlalchemy.DateTime,
                                nullable=False, onupdate=now, **default_now)
                            )

with engine.begin() as conn:
    conn.execute(sqlalchemy.text(
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))

metadata.create_all(engine)
