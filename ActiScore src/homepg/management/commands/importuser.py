import csv
from django.core.management.base import BaseCommand, CommandError
from homepg.models import CustomUser, Student,Teacher


class Command(BaseCommand):
    help = "Adds data from a csv file into database"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    # Skip the header row
                    line_count += 1
                else:
                    # Assuming your CSV file has data in the format: username, email, password, student_name, points
                    username = row[0]
                    regno = row[1].lower()
                    batch = row[2]
                    password = row[3]
                    
                    # Create or get the CustomUser object
                    custom_user = CustomUser.objects.create_user(username=username, password=password,verified=True)
                    custom_user.save()
                    teacher = Teacher.objects.get(batch=batch)
                    student= Student.objects.create(user=custom_user, name=username, batch=batch, regno=regno,teacher=teacher)
                    student.save()
                    line_count += 1
            
            print(f'Processed {line_count - 1} lines.')