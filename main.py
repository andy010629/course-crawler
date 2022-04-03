import pymongo
from crawler import MCUCoursesCrawler

db_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = db_client["mcu-up"]
mycol = db['test']


course_data = MCUCoursesCrawler()

cursor = mycol.find({})
courseData_dict = dict()
for course in cursor:
  courseData_dict[course['super_hash']] =  course

for course in course_data:
  courseData_dict[course['super_hash']] = course

insert_data = list(courseData_dict.values())

mycol.drop()
mycol.insert_many(insert_data)

