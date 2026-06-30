from faker import Faker
import factory
from sqlmodel import Field, SQLModel, create_engine, Session

DB_URL = "sqlite:///database.sqlite"


def create_faker() -> Faker:
    Faker.seed(42)
    fake = Faker(locale="zu_ZA")
    return fake


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

    fake = create_faker()
    name = fake.name()
    prefix = fake.prefix()
    firtname = fake.first_name()
    lastname = fake.last_name()
    address = fake.address()
    addunit = fake.administrative_unit()
    building = fake.building_number()
    city = fake.city_name()
    postcode = fake.postcode()
    province = fake.province()
    language = fake.language_name()
    email = fake.email()
    desc = fake.text(max_nb_chars=100)
    country = fake.country()
    latitude = fake.latitude()
    longitude = fake.longitude()
    url = fake.url()
    quote = fake.sentence()
    phone_number = fake.phone_number()
    job = fake.job()
    dob = fake.date_of_birth(minimum_age=16)


def main():
    print("Hello from datafaker!")

    engine = create_engine(url=DB_URL)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = UserModelFactory.create()
        session.add(user)
        session.commit()


if __name__ == "__main__":
    main()
