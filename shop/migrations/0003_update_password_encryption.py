from django.db import migrations, models

from shop.models import before_user_save


def update_password_encryption(app, schema_editor):
    User = app.get_model('shop', 'User')
    db_alias = schema_editor.connection.alias

    for user in User.objects.using(db_alias):
        before_user_save(None, user)
        user.save()


def reverse_password_encryption(_, __):
    # 单向加密，不可回滚
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_add_usertype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=60),
        ),
        migrations.RunPython(update_password_encryption, reverse_password_encryption),
    ]
