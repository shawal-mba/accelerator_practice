import os
import factory

from logging import Logger
from sqlmodel import Field, SQLModel, create_engine, Session

DB_URL = "sqlite:///database.sqlite"
logger = Logger(name=__name__, level=1)


class UserModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    prefix: str
    firtname: str
    lastname: str
    address: str
    addunit: str
    building: str
    city: str
    postcode: str
    province: str
    language: str
    email: str
    desc: str
    country: str
    latitude: float
    longitude: float
    url: str
    quote: str
    phone_number: str
    job: str
    dob: str


class UserModelFactory(factory.Factory):
    class Meta:
        model = UserModel

    name = factory.Faker("name", locale="zu_ZA")
    prefix = factory.Faker("prefix", locale="zu_ZA")
    firtname = factory.Faker("first_name", locale="zu_ZA")
    lastname = factory.Faker("last_name", locale="zu_ZA")
    address = factory.Faker("address", locale="zu_ZA")
    addunit = factory.Faker("administrative_unit", locale="zu_ZA")
    building = factory.Faker("building_number", locale="zu_ZA")
    city = factory.Faker("city_name", locale="zu_ZA")
    postcode = factory.Faker("postcode", locale="zu_ZA")
    province = factory.Faker("province", locale="zu_ZA")
    language = factory.Faker("language_name", locale="zu_ZA")
    email = factory.Faker("email", locale="zu_ZA")
    desc = factory.Faker("text", max_nb_chars=100, locale="zu_ZA")
    country = factory.Faker("country", locale="zu_ZA")
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
    url = factory.Faker("url")
    quote = factory.Faker("sentence")
    phone_number = factory.Faker("phone_number", locale="zu_ZA")
    job = factory.Faker("job", locale="zu_ZA")
    dob = factory.Faker("date_of_birth", minimum_age=16)


def main():
    logger.log(level=1, msg="Hello from datafaker!")
    db_file = "database.sqlite"

    if os.path.exists(db_file):
        os.remove(db_file)
        logger.log(level=1, msg="Deletes old db file")

    engine = create_engine(url=DB_URL)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for _ in range(500):
            user = UserModelFactory.create()
            session.add(user)
            session.commit()


if __name__ == "__main__":
    main()
