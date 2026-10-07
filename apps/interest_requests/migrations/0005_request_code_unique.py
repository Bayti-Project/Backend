from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interest_requests', '0004_alter_interestrequest_request_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interestrequest',
            name='request_code',
            field=models.CharField(
                max_length=20,
                unique=True,
                null=True,
                blank=True,
                editable=False,
            ),
        ),
    ]