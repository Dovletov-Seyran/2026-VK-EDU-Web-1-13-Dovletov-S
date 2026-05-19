import random
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils.text import slugify
from core.models import Profile
from questions.models import Question, Answer, Tag, QuestionLike, AnswerLike
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = "Fill database with data"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help="Coefficient for data generation")

    def handle(self, *args, **options):
        ratio = options["ratio"]

        self.stdout.write("Checking migrations...")
        call_command("migrate")

        self.clear_data()
        users = self.create_users(ratio)
        self.create_profiles(users)
        tags = self.create_tags(ratio)
        questions = self.create_questions(ratio, users)
        self.add_tags_to_questions(questions, tags)
        answers = self.create_answers(ratio, questions, users)
        self.create_question_likes(ratio, users, questions)
        self.create_answer_likes(ratio, users, answers)

        self.stdout.write(self.style.SUCCESS("Done!"))

    def clear_data(self):
        self.stdout.write("Clearing old data...")
        AnswerLike.objects.all().delete()
        QuestionLike.objects.all().delete()
        Answer.objects.all().delete()
        Question.objects.all().delete()
        Tag.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self, ratio):
        self.stdout.write("Creating users...")
        users = []
        for i in range(ratio):
            users.append(
                User(
                    username=f"user_{i}",
                    email=f"user_{i}@example.com",
                    password="password123",
                )
            )
        User.objects.bulk_create(users, batch_size=10000)
        users = list(User.objects.all())
        self.stdout.write(f"Created {len(users)} users")
        return users

    def create_profiles(self, users):
        self.stdout.write("Creating profiles...")
        profiles = [Profile(user=user) for user in users]
        Profile.objects.bulk_create(profiles, batch_size=10000)
        self.stdout.write(f"Created {len(profiles)} profiles")

    def create_tags(self, ratio):
        self.stdout.write("Creating tags...")
        tags = []
        for i in range(ratio):
            title = f"{fake.word()}_{i}"
            tags.append(Tag(title=title, slug=slugify(title)))
        Tag.objects.bulk_create(tags, batch_size=10000)
        tags = list(Tag.objects.all())
        self.stdout.write(f"Created {len(tags)} tags")
        return tags

    def create_questions(self, ratio, users):
        self.stdout.write("Creating questions...")
        questions = []
        for i in range(ratio * 10):
            questions.append(
                Question(
                    title=fake.sentence()[:255],
                    slug=f"question-{i}",
                    text=fake.text(),
                    user=random.choice(users),
                )
            )
        Question.objects.bulk_create(questions, batch_size=10000)
        questions = list(Question.objects.all())
        self.stdout.write(f"Created {len(questions)} questions")
        return questions

    def add_tags_to_questions(self, questions, tags):
        self.stdout.write("Adding tags to questions...")
        through_model = Question.tags.through
        question_tags = []
        for question in questions:
            random_tags = random.sample(tags, k=min(3, len(tags)))
            for tag in random_tags:
                question_tags.append(
                    through_model(question_id=question.id, tag_id=tag.id)
                )
        through_model.objects.bulk_create(
            question_tags, ignore_conflicts=True, batch_size=10000
        )
        self.stdout.write("Added tags to questions")

    def create_answers(self, ratio, questions, users):
        self.stdout.write("Creating answers...")
        answers = []
        for i in range(ratio * 100):
            answers.append(
                Answer(
                    text=fake.text(),
                    question=random.choice(questions),
                    user=random.choice(users),
                )
            )
        Answer.objects.bulk_create(answers, batch_size=10000)
        answers = list(Answer.objects.all())
        self.stdout.write(f"Created {len(answers)} answers")
        return answers

    def create_question_likes(self, ratio, users, questions):
        self.stdout.write("Creating question likes...")
        question_likes = set()
        question_likes_objects = []
        target = ratio * 100
        while len(question_likes) < target:
            user = random.choice(users)
            question = random.choice(questions)
            pair = (user.id, question.id)
            if pair not in question_likes:
                question_likes.add(pair)
                question_likes_objects.append(
                    QuestionLike(user_id=user.id, question_id=question.id)
                )
        QuestionLike.objects.bulk_create(
            question_likes_objects, ignore_conflicts=True, batch_size=10000
        )
        self.stdout.write(f"Created {len(question_likes_objects)} question likes")

    def create_answer_likes(self, ratio, users, answers):
        self.stdout.write("Creating answer likes...")
        answer_likes = set()
        answer_likes_objects = []
        target = ratio * 100
        while len(answer_likes) < target:
            user = random.choice(users)
            answer = random.choice(answers)
            pair = (user.id, answer.id)
            if pair not in answer_likes:
                answer_likes.add(pair)
                answer_likes_objects.append(
                    AnswerLike(user_id=user.id, answer_id=answer.id)
                )
        AnswerLike.objects.bulk_create(
            answer_likes_objects, ignore_conflicts=True, batch_size=10000
        )
        self.stdout.write(f"Created {len(answer_likes_objects)} answer likes")
