from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0019_remove_userlearningtrack_progression'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlearningtrack',
            name='current_level',
            field=models.CharField(
                choices=[('explorer', 'Explorer'), ('builder', 'Builder'), ('master', 'Master')],
                default='explorer',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='userlearningtrack',
            name='progress_score',
            field=models.IntegerField(default=0),
        ),
        migrations.RenameField(
            model_name='task',
            old_name='starter_code',
            new_name='task_code',
        ),
        migrations.RemoveField(
            model_name='task',
            name='task',
        ),
        migrations.AddField(
            model_name='task',
            name='is_reinforcement',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='weak_topic',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
