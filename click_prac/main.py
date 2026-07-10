import click


@click.command()
@click.option("--count", default=1, help="number of greetings")
@click.option("--name", prompt="your name", help="number of greetings")
def main(count, name):
    for x in range(count):
        click.echo(f"Hello {name}")


if __name__ == "__main__":
    main()
