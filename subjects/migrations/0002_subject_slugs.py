"""Заполнить уникальные slug до включения NOT NULL и UNIQUE."""
from django.db import migrations, models
from django.utils.text import slugify
from unidecode import unidecode


def populate_slugs(apps, schema_editor):
    Subject = apps.get_model("subjects", "Subject")
    items = Subject.objects.using(schema_editor.connection.alias)
    for item in items.all().order_by("pk"):
        base = slugify(unidecode(item.name))[:140] or "subject"
        items.filter(pk=item.pk).update(slug=f"{base}-{item.pk}")


class Migration(migrations.Migration):
    dependencies = [("subjects", "0001_initial")]
    operations = [
        migrations.AddField(model_name="subject", name="slug", field=models.SlugField(
            max_length=180, null=True, editable=False, verbose_name="URL-идентификатор")),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(model_name="subject", name="slug", field=models.SlugField(
            max_length=180, unique=True, editable=False, verbose_name="URL-идентификатор")),
    ]
