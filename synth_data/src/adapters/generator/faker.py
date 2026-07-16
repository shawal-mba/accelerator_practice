"""Faker-based data generator — default implementation of the DataGenerator port."""

from __future__ import annotations

from datetime import date, datetime, time

from faker import Faker


class FakerAdapter:
    """Adapts Faker to the DataGenerator port.

    Usage::

        from src.adapters.generator.faker import FakerAdapter
        gen = FakerAdapter(locale="zu_ZA")
        matchers = build_matchers(gen)
    """

    def __init__(self, locale: str = "zu_ZA") -> None:
        self._fake = Faker(locale)

    def word(self) -> str:
        return self._fake.word()

    def words(self, nb: int = 3) -> list[str]:
        return self._fake.words(nb=nb)

    def name(self) -> str:
        return self._fake.name()

    def first_name(self) -> str:
        return self._fake.first_name()

    def last_name(self) -> str:
        return self._fake.last_name()

    def email(self) -> str:
        return self._fake.email()

    def phone_number(self) -> str:
        return self._fake.phone_number()

    def street_address(self) -> str:
        return self._fake.street_address()

    def city(self) -> str:
        return self._fake.city()

    def province(self) -> str:
        return self._fake.province()

    def postcode(self) -> str:
        return self._fake.postcode()

    def country(self) -> str:
        return self._fake.country()

    def country_code(self) -> str:
        return self._fake.country_code()

    def latitude(self) -> str:
        return self._fake.latitude()

    def longitude(self) -> str:
        return self._fake.longitude()

    def company(self) -> str:
        return self._fake.company()

    def job(self) -> str:
        return self._fake.job()

    def pyfloat(self, min_value: float = 0, max_value: float = 1) -> float:
        return self._fake.pyfloat(min_value=min_value, max_value=max_value)

    def pyint(self, min_value: int = 0, max_value: int = 1) -> int:
        return self._fake.pyint(min_value=min_value, max_value=max_value)

    def credit_card_number(self) -> str:
        return self._fake.credit_card_number()

    def iban(self) -> str:
        return self._fake.iban()

    def currency_code(self) -> str:
        return self._fake.currency_code()

    def ssn(self) -> str:
        return self._fake.ssn()

    def uuid4(self) -> str:
        return self._fake.uuid4()

    def isbn13(self) -> str:
        return self._fake.isbn13()

    def mac_address(self) -> str:
        return self._fake.mac_address()

    def date_time_between(self, start_date: str = "-30y", end_date: str = "now") -> datetime:
        return self._fake.date_time_between(start_date=start_date, end_date=end_date)

    def date_between(self, start_date: str = "-30y", end_date: str = "today") -> date:
        return self._fake.date_between(start_date=start_date, end_date=end_date)

    def year(self) -> str:
        return str(self._fake.year())

    def month(self) -> str:
        return self._fake.month()

    def url(self) -> str:
        return self._fake.url()

    def domain_name(self) -> str:
        return self._fake.domain_name()

    def ipv4(self) -> str:
        return self._fake.ipv4()

    def slug(self) -> str:
        return self._fake.slug()

    def password(self) -> str:
        return self._fake.password()

    def sha256(self) -> str:
        return self._fake.sha256()

    def mime_type(self) -> str:
        return self._fake.mime_type()

    def file_extension(self) -> str:
        return self._fake.file_extension()

    def timezone(self) -> str:
        return self._fake.timezone()

    def sentence(self) -> str:
        return self._fake.sentence()

    def paragraph(self) -> str:
        return self._fake.paragraph()

    def hex_color(self) -> str:
        return self._fake.hex_color()

    def binary(self, length: int = 10) -> bytes:
        return self._fake.binary(length)

    def json(self) -> str:
        return self._fake.json()

    def xml(self) -> str:
        return self._fake.xml()

    def text(self, max_nb_chars: int = 200) -> str:
        return self._fake.text(max_nb_chars=max_nb_chars)

    def time_object(self) -> time:
        return self._fake.time_object()
