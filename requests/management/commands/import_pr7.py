"""Перенос данных из read-only источника ПР7 в модели Django."""
from pathlib import Path
import sqlite3

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from db.inspect_source_db import SOURCE_DB
from db.transfer_to_orm import transfer_to_orm


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("--source", type=Path, default=SOURCE_DB)
        parser.add_argument("--only-if-empty", action="store_true")

    def handle(self, *args, **options):
        try:
            result = transfer_to_orm(options["source"], only_if_empty=options["only_if_empty"])
        except (ValueError, ValidationError, DatabaseError, OSError, sqlite3.Error) as exception:
            raise CommandError(str(exception)) from exception
        self.stdout.write(self.style.SUCCESS(f"Перенос ПР7: {result}"))
