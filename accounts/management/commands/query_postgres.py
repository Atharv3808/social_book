from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
from sqlalchemy import create_engine, text


def build_postgres_url_from_settings():
    db = settings.DATABASES.get("default", {})
    engine = db.get("ENGINE", "")
    if "postgresql" not in engine:
        return None
    name = db.get("NAME")
    user = db.get("USER")
    password = db.get("PASSWORD")
    host = db.get("HOST", "localhost")
    port = db.get("PORT", 5432)
    if not all([name, user]):
        return None
    return f"postgresql+psycopg2://{user}:{password or ''}@{host}:{port}/{name}"


class Command(BaseCommand):
    help = "Query a local Postgres database using SQLAlchemy and print results"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sql",
            default="SELECT NOW() as now",
            help="SQL query to execute",
        )
        parser.add_argument(
            "--url",
            default=None,
            help=(
                "SQLAlchemy database URL. If omitted, will attempt to use "
                "DATABASE_URL env var or build from Django settings when ENGINE is PostgreSQL."
            ),
        )

    def handle(self, *args, **options):
        sql = options["sql"]
        url = options["url"] or os.environ.get("DATABASE_URL")
        if not url:
            url = build_postgres_url_from_settings()

        if not url:
            raise CommandError(
                "No Postgres URL provided and default DB is not Postgres. "
                "Provide --url like postgresql+psycopg2://user:pass@localhost:5432/dbname"
            )

        try:
            engine = create_engine(url)
        except Exception as e:
            raise CommandError(f"Failed to create engine: {e}")

        self.stdout.write(self.style.NOTICE(f"Connecting to: {url}"))
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                keys = result.keys()
                self.stdout.write(self.style.SUCCESS(f"Columns: {', '.join(keys)}"))
                count = 0
                for row in result.mappings():
                    count += 1
                    # Print as key=value pairs
                    line = ", ".join([f"{k}={row[k]}" for k in keys])
                    self.stdout.write(line)
                self.stdout.write(self.style.SUCCESS(f"Rows: {count}"))
        except Exception as e:
            raise CommandError(f"Query failed: {e}")