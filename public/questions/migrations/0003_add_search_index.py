from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0002_answerlike_vote_questionlike_vote"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE INDEX question_search_idx
                ON questions_question
                USING gin (
                    to_tsvector('russian', coalesce(title, '') || ' ' || coalesce(text, ''))
                );
            """,
            reverse_sql="DROP INDEX IF EXISTS question_search_idx;",
        ),
    ]
