from django.db import migrations, models

import django.db.models.deletion


def init_usertype(app, schema_editor):
    UserType = app.get_model('shop', 'UserType')
    db_alias = schema_editor.connection.alias

    UserType.objects.using(db_alias).bulk_create([
        UserType(pk=1, typename='admin', description='管理员，拥有最高权限。'),
        UserType(pk=2, typename='seller', description='商户，拥有管理商铺的权限。'),
        UserType(pk=3, typename='normal', description='普通用户，拥有购买商品权限。'),
    ])


def reverse_usertype(app, schema_editor):
    UserType = app.get_model('shop', 'UserType')
    db_alias = schema_editor.connection.alias

    UserType.objects.using(db_alias).filter(typename='admin').delete()
    UserType.objects.using(db_alias).filter(typename='seller').delete()
    UserType.objects.using(db_alias).filter(typename='normal').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typename', models.CharField(max_length=20, unique=True)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        # TODO: 初始化用户类型之前该表还未建立，导致迁移出错（需要查看文档确定），建议分开两次迁移。
        migrations.RunPython(init_usertype, reverse_usertype),
        migrations.AddField(
            model_name='user',
            name='type',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.PROTECT, to='shop.UserType'),
        ),
    ]
