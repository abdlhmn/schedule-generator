import json
from datetime import datetime, timedelta
from itertools import product

class All_Subjects:
    def __init__(self, data, lab=False):
        self.subject = data['subject']
        self.class_length = data['class length']
        self.instructors = data['instructors']
        # e.g. {"Mohammad": ["MW 09:30", "MW 12:30"], "Denys Dutykh": ["MW 12:30", "TT14:00"], "Ameena": ["TT 12:30"]}
        self.all_cls = []
        self.lab = lab
        self.generate_classes()

    def generate_classes(self):
        for instructor, times in self.instructors.items():
            for time in times:
                days, start_time = time.split(' ')
                if not self.lab:
                    days = days[0], days[1:]
                ts = add_time(start_time, self.class_length)
                self.all_cls.append(Lessons(instructor, self.subject, ts, days, self.lab))

    def __repr__(self):
        return self.subject
    

class Lessons:
    def __init__(self, instructor, subject, time_span, days, lab=False):
        self.instructor = instructor
        self.subject = subject
        self.time_span = time_span
        self.lab = lab
        self.days = days
   
    def __repr__(self):
        t1 = self.time_span[0].strftime('%I:%M %p')
        t2 = self.time_span[1].strftime('%I:%M %p')
        return f'{self.subject} {self.days} {t1}-{t2}'


def add_time(initial, lesson_length):
    initial_time = datetime.strptime(initial, '%H:%M').time()
    mins = timedelta(minutes=lesson_length)
    end_time = (datetime.combine(datetime.min, initial_time) + mins).time()
    return initial_time, end_time


# 8-9 and 8:30-9:30
def validate_schedule(lst):
    lst = sorted(lst, key=lambda z: z.time_span[0])
    organized_schedule = schedule_generator(lst)
    for lessons in organized_schedule.values():
        for i in range(1, len(lessons)):
            if lessons[i].time_span[0] < lessons[i-1].time_span[1]:
                return 'invalid schedule'
    return organized_schedule


def schedule_generator(schedule):
    weekly_schedule = {
        'M' : [],
        'T' : [],
        'W': [],
        'Th': [],
        }
    for session in schedule:
        if session.lab:
            weekly_schedule[session.days].append(session)
        else:
            for day in session.days:
                weekly_schedule[day].append(session)
    return weekly_schedule


def print_schedules(schedules):
    for n, schedule in enumerate(schedules, 1):
        print(f'schedule {n}:')
        for day, lessons in schedule.items():
            print(day)
            print(*lessons, sep='|')
        print('\n'*3)


all_lessons = dict()
# dictionary containing subject name, and the class object

with open('classes.json') as f:
    data = json.load(f)
LESSONS_ID = list(data.keys())
for lesson_id in LESSONS_ID:
    if 'lab' in lesson_id:
        all_lessons[data[lesson_id]['subject']] = All_Subjects(data[lesson_id], lab=True)
    else:
        all_lessons[data[lesson_id]['subject']] = All_Subjects(data[lesson_id])
all_classes = list(all_lessons.values())

all_possibilities = list(product(*[obj.all_cls for obj in all_classes]))
final_schedules = []
for possibility in all_possibilities:
    sched = validate_schedule(possibility)
    if sched != 'invalid schedule':
        final_schedules.append(sched)

all_sched = [pompom.values() for pompom in final_schedules]
print_schedules(final_schedules)
print(len(all_sched), len(set(all_sched)))
