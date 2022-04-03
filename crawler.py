import requests
from bs4 import BeautifulSoup
from format import *
import hashlib
import os



def getSch():
    res = requests.get(
        "https://www.mcu.edu.tw/student/new-query/sel-query/qslist.asp")
    res.encoding = 'big5-hkscs'
    soup = BeautifulSoup(res.text, 'html.parser')
    sch_tags = soup.select("[name=sch]")[0].find_all("option")
    sch_list = [{'id': sch.get('value'), 'name': sch.text.replace('\xa0', '')} for sch in sch_tags[1:]]
    return sch_list

def MCUCoursesCrawler():
    print("Start crouses crawler...")

    url_c = "https://www.mcu.edu.tw/student/new-query/sel-query/qslist_1.asp"
    request_session = requests.session()
    all_courses = list()

    for ggdb in [0]:  # 當學期 0 上學期 1 下學期 2 
        for sch in getSch():
            
            # get source
            if os.path.isfile(f'{sch["name"]}.txt'):
                res = open(f'{sch["name"]}.txt', encoding='utf-8')
            else:
                res = request_session.post(
                    url_c, data={"sch": sch['id']}, cookies={"ggdb": str(ggdb)})
                res.encoding = 'big5-hkscs'
                open(f'{sch["name"]}.txt', 'w',encoding='utf-8').write(res.text)
                res = res.text
            soup = BeautifulSoup(res, 'lxml')

            # parse data
            course_tags = soup.select('tr')[1:]
          
            for course_tag in course_tags:
                course_data = [(t.text) for t in course_tag.find_all('td')]
                course_id, course_name = clean_special_char(course_data[1].split(
                    ' ')[0]), clean_special_char(course_data[1].split(' ')[1])

                if course_name in ["週會", '班會']: continue
                    
                class_id = clean_special_char(course_data[2]).split(' ')[0]
                stu_count,stu_limit = -1,int(course_data[3].split('／')[0])
                teacher_time =  teacher_time_format(course_data[4], course_data[5])
                teacher_list = teacher_format(course_data[4])

                if course_data[4].find("實習") != -1 and course_data[4].find("實習") < course_data[4].find("正課"):
                    raise Exception('ㄟ嘿嘿順序跑掉要重寫摟 ' + course_data[4])

                course_grade = clean_special_char(course_data[6])
                classroom,campus = classroomCampus_format(course_data[7])
                units = int(clean_special_char(course_data[9]))
                special_type = clean_special_char(course_data[10])
                comments = course_data[13]

                if clean_special_char(course_data[11]) == 'Y':
                    isgraduate = True
                elif clean_special_char(course_data[11]) == 'N':
                    isgraduate = False
                else:
                    raise Exception('error isgraduate  type' +
                                    clean_special_char(course_data[11]))

                if clean_special_char(course_data[8]) == "通識":
                    course_type = 0
                elif clean_special_char(course_data[8]) == "必修":
                    course_type = 1
                elif clean_special_char(course_data[8]) == "選修":
                    course_type = 2
                elif clean_special_char(course_data[8]) == "教育":
                    course_type = 3
                else:
                    raise Exception('error corse_type ' + clean_special_char(course_data[8]))

                if clean_special_char(course_data[12]) == "全學年":
                    semester = 0 
                elif clean_special_char(course_data[12]) == "上學期":
                    semester = 1
                elif clean_special_char(course_data[12]) == "下學期":
                    semester = 2
                else:
                    raise Exception('error semester ' + clean_special_char(course_data[12]))

            
                # make md5 hash
                course_hash = str(hashlib.md5(course_name.encode('utf-8')).hexdigest())
                super_str = course_hash
                for ts in teacher_time:
                    super_str += ts['teacher_hash']
                super_hash = hashlib.md5(super_str.encode('utf-8')).hexdigest()

                course = {
                    'course_id': course_id,
                    'course_name': course_name,
                    'class_id': class_id,
                    # 'stu_limit': stu_limit,
                    # 'stu_count': stu_count,
                    # 'teacher_time': teacher_time,
                    'teacher_list': teacher_list,
                    'course_grade': course_grade,
                    'course_type': course_type,
                    'classroom': classroom,
                    'campus':campus,
                    'semester': semester,
                    'units': units,
                    'special_type': special_type,
                    'isgraduate': isgraduate,
                    'comments': comments,
                    'course_hash': course_hash,
                    'super_hash': super_hash,
                }

                all_courses.append(course)
    return all_courses
