from django.db import migrations
 
 
class Migration(migrations.Migration):
 
    dependencies = [
        ('account', '0007_companyrequest'),
    ]
 
    operations = [
        migrations.RenameModel(
            old_name='CustomerRequest',
            new_name='UserRequest',
        ),
    ]