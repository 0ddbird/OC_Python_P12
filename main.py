import sentry_sdk
import typer
from rich import print
from sqlmodel import create_engine

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
app = typer.Typer()


if __name__ == "__main__":
    try:
        app()
    except AssertionError as e:
        print(str(e))
        sentry_sdk.capture_exception(e)
