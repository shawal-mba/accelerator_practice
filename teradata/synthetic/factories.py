import factory
from faker import Faker
from sqlmodel import SQLModel

from .types import ColumnMeta, get_faker_strategy

fake = Faker()


def _snake_to_pascal(name: str) -> str:
    return "".join(word.capitalize() for word in name.split("_"))


def build_factory(model: type[SQLModel]) -> type[factory.Factory]:
    field_map = model._field_map  # type: ignore
    table_key = model._table_key  # type: ignore

    attrs: dict[str, Any] = {}
    for field_name, meta in field_map.items():
        col = ColumnMeta(
            name=meta["td_name"],
            data_type=meta["data_type"],
            column_type="",
            is_nullable=meta["nullable"],
        )
        strategy = get_faker_strategy(col)
        gen = strategy.generate
        attrs[field_name] = factory.LazyFunction(gen)

    factory_name = _snake_to_pascal(table_key.replace(".", "_")) + "Factory"

    meta_class = type("Meta", (), {"model": model})
    attrs["Meta"] = meta_class
    factory_class = type(factory_name, (factory.Factory,), attrs)
    return factory_class


def create_factories(
    models: dict[str, type[SQLModel]],
) -> dict[str, type[factory.Factory]]:
    factories: dict[str, type[factory.Factory]] = {}
    for key, model in models.items():
        factories[key] = build_factory(model)
    return factories
