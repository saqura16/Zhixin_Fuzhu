import json
import os
import sys
import time
from datetime import datetime, timedelta

import requests


def get_num(data):  # 获取作业数量
    num = -1
    for i in range(130):
        try:
            s = data['data'][i]
        except:
            num = i
        if num == i:
            break
    return num


def get_qusetionnum(page):
    number = -1
    for i in range(800):
        try:
            s = page['data']['questionSets'][0]['questions'][i]
        except Exception:
            number = i
        if number == i:
            break
    return number


def get_chiose_num(page):
    number = -1
    for i in range(10):
        try:
            s = page['data']['questionSets'][0]['questions'][0]['answer'][i]
        except Exception:
            number = i
        if number == i:
            break
    return number


def show_homework(homework_id, course_id_list, headers):  # 功能1,无分数展示作业
    work_detail_url = str(
        'https://cyber-tea-platform.anrunlu.net/stu/homework/' + str(course_id_list[homework_id]))
    work_detail = requests.get(url=work_detail_url, headers=headers).json()
    content = work_detail['data']['questionSets'][0]['questions'][0]['content']
    questions_num = get_qusetionnum(work_detail)
    for i in range(questions_num):
        print('-' * 60)
        content = work_detail['data']['questionSets'][0]['questions'][i]['content']
        type_ = work_detail['data']['questionSets'][0]['questions'][i]['type']
        print('[', type_, ']  ', i + 1, '.', content.strip(), sep='')
        answer_chose_num = get_chiose_num(work_detail)
        if type_ != '解答':
            for j in range(answer_chose_num):
                answer = work_detail['data']['questionSets'][0]['questions'][i]['answer'][j]['content'].strip(
                )
                mark = work_detail['data']['questionSets'][0]['questions'][i]['answer'][j]['mark'].strip(
                )
                print(mark + ': ' + answer, sep='', end='        ')
        print()


def show_homework_(homework_id, course_id_list, headers):  # 功能2,有分数展示作业
    work_detail_url = str(
        'https://cyber-tea-platform.anrunlu.net/stu/homework/' + str(course_id_list[homework_id]))
    work_detail = requests.get(url=work_detail_url, headers=headers).json()
    content = work_detail['data']['questionSets'][0]['questions'][0]['content']
    questions_num = get_qusetionnum(work_detail)
    for i in range(questions_num):
        try:
            print('-' * 60)  # 题与题之间的分界符
            # 题目类型
            type_ = work_detail['data']['questionSets'][0]['questions'][i]['type']
            if type_ == '解答':  # 大题
                # 题目
                content = work_detail['data']['questionSets'][0]['questions'][i]['content']
                my_answer = work_detail['data']['questionSets'][0]['questions'][i]['studentQA'][0]['stuAnswer'][0][
                    'content'].strip()  # 我的答案
                # 得分
                score = work_detail["data"]['questionSets'][0]['questions'][i]['studentQA'][0]['score']
                print('[', type_, ']  ', i + 1, '.',
                      content.strip(), sep='', end='')
            else:  # 选择和判断
                # 题目
                content = work_detail['data']['questionSets'][0]['questions'][i]['content']
                my_answer = work_detail['data']['questionSets'][0]['questions'][i]['studentQA'][0]['stuAnswer'][0][
                    'mark'].strip()  # 我的答案
                # 得分
                score = work_detail["data"]['questionSets'][0]['questions'][i]['studentQA'][0]['score']
                print('[', type_, ']  ', i + 1, '.',
                      content.strip(), sep='', end='')

            if score != 0:  # 输出分数
                print('(', my_answer, ')''  score: ', round(score, 2))
            else:
                print('(', my_answer, ')''  score: ', round(score, 2))
            answer_chose_num = get_chiose_num(work_detail)
            if type_ == '解答':  # 输出解答题
                answer = work_detail['data']['questionSets'][0]['questions'][i]['answer'][0]['content'].strip(
                )
                mark = work_detail['data']['questionSets'][0]['questions'][i]['answer'][0]['mark'].strip(
                )
                print(mark + ': ' + answer, sep='', end='        ')
            else:  # 输出(非解答题选项)
                for j in range(answer_chose_num):  # 输出选项
                    answer = work_detail['data']['questionSets'][0]['questions'][i]['answer'][j]['content'].strip(
                    )
                    mark = work_detail['data']['questionSets'][0]['questions'][i]['answer'][j]['mark'].strip(
                    )
                    print(mark + ': ' + answer, sep='', end='        ')
            print()
        except:
            print(i, '题目未作答或出现错误')


def find_no_answer(work_isend, headers):
    not_fin = {}
    num_count = 1
    for i, j in work_isend.items():
        count = 0
        # 构造未截至作业的url
        print('正在检查第', num_count, '项', sep='')
        url = 'https://cyber-tea-platform.anrunlu.net/stu/homework/' + str(j)
        homework = requests.get(url=url, headers=headers).json()
        title = str(i) + '.' + str(homework['data']['title']).strip()
        num = get_qusetionnum(homework)
        for k in range(num):
            try:
                homework['data']['questionSets'][0]['questions'][k]['studentQA'][0]
                count += 1
            except:
                continue
        if count / num != 1:
            not_fin.setdefault(title, (count / num))
        else:
            pass
        num_count += 1
    for i, j in not_fin.items():
        print(i, '完成度:', str(j * 100) + '%', sep="    ")
        # data.questionSets[0].questions[0].studentQA 如果作答,存在QA
        # data.title #作业name


def Ai_write(course_id, Au):  # 考虑多线程
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
        'Authorization': Au,
        'Content-Type': 'application/json;charset=UTF-8'}
    # course_id_list,课程id在这里卖,有了
    # questionset_id位置:      data.questionSets[0]._id
    # 题目id :data.questionSets[0].questions[0].id
    homeworkurl = 'https://cyber-tea-platform.anrunlu.net/stu/homework/' + \
        str(course_id)
    data = requests.get(url=homeworkurl, headers=headers).json()  # 获取题目页面信息
    questions_num = get_qusetionnum(data)
    questions_id_list = []
    questionset_id = data['data']['questionSets'][0]['_id']
    # questionset_id=data.questionSets[0]._id
    for i in range(questions_num):  # 获取所有题目id
        d = data['data']['questionSets'][0]['questions'][i]['id']
        questions_id_list.append(d)

    answerforquestionURL = 'https://cyber-tea-platform.anrunlu.net/stu/question/answerForQuestion'  # 提交答案的URL
    # for w in range(questions_num):  #对于所有题来说
    for w in range(questions_num):  # 对于所有题来说
        print('正在写第', w, '题', sep='')
        kwargs_A = {'homework_id': course_id, 'questionSet_id': questionset_id, 'question_id': questions_id_list[w],
                    'stuAnswer': [{"mark": "A"}]}
        kwargs_B = {'homework_id': course_id, 'questionSet_id': questionset_id, 'question_id': questions_id_list[w],
                    'stuAnswer': [{"mark": "B"}]}
        kwargs_C = {'homework_id': course_id, 'questionSet_id': questionset_id, 'question_id': questions_id_list[w],
                    'stuAnswer': [{"mark": "C"}]}
        kwargs_D = {'homework_id': course_id, 'questionSet_id': questionset_id, 'question_id': questions_id_list[w],
                    'stuAnswer': [{"mark": "D"}]}
        kwargs_A1 = json.dumps(kwargs_A)
        kwargs_B1 = json.dumps(kwargs_B)
        kwargs_C1 = json.dumps(kwargs_C)
        kwargs_D1 = json.dumps(kwargs_D)
        kwargs_list = []

        kwargs_list.append(kwargs_B1)
        kwargs_list.append(kwargs_C1)
        kwargs_list.append(kwargs_D1)
        s = requests.post(url=answerforquestionURL,
                          headers=headers, data=kwargs_A1)
        c = 0
        # print(s.json(),s.status_code)
        while get_score(homeworkurl, headers, w) == 0:  # 分数为0,选项错误，换选项
            try:
                s = requests.post(url=answerforquestionURL,
                                  headers=headers, data=kwargs_list[c])
                c = c + 1
            except:
                pass
        print('第', w, '题已写完', sep='')


def get_score(homeworkurl, headers, num):
    score = 0
    try:
        data = requests.get(url=homeworkurl, headers=headers).json()
        # 分数data.questionSets[0].questions[5].studentQA[0].score
        score = data['data']['questionSets'][0]['questions'][num]['studentQA'][0]['score']
    except:
        pass
    return score


def output_word(homework_id, course_id_list, headers):
    # 保存到文件
    work_detail_url = str(
        'https://cyber-tea-platform.anrunlu.net/stu/homework/' + str(course_id_list[homework_id]))
    work_detail = requests.get(url=work_detail_url, headers=headers).json()
    title = str(homework_id) + '.' + str(work_detail['data']['title']).strip()
    print('正在输出', title, '...')
    content = work_detail['data']['questionSets'][0]['questions'][0]['content']
    questions_num = get_qusetionnum(work_detail)
    with open(str(title) + '.txt', mode='w', encoding="utf-8") as f:
        count = 0
        for i in range(questions_num):
            content = work_detail['data']['questionSets'][0]['questions'][i]['content']
            type_ = work_detail['data']['questionSets'][0]['questions'][i]['type']
            list_ = [count, '.', '[', type_, ']  ',
                     i + 1, '.', content.strip()]
            for ss in list_:
                ss = str(ss)
                f.write(ss)
            answer_chose_num = get_chiose_num(work_detail)
            if type_ != '解答':
                f.write('\n')
                for j in range(answer_chose_num):
                    answer = work_detail['data']['questionSets'][0]['questions'][i]['answer'][j]['content'].strip(
                    )
                    mark = work_detail['data']['questionSets'][0]['questions'][i]['answer'][j]['mark'].strip(
                    )
                    f.write(mark)
                    f.write(': ')
                    f.write(answer)
                    f.write('\n')
            f.write('\n')
            count += 1
    with open('[答案]' + str(title) + '.txt', mode='w', encoding="utf-8") as f:
        f.write('score为0代表当时做这个题的时候选择错误,所以答案也是错的哦!')
        f.write('\n')
        count_ = 0
        for k1 in range(questions_num):
            try:
                # 题目类型
                type_ = work_detail['data']['questionSets'][0]['questions'][k1]['type']
                if type_ != '解答':
                    my_answer = work_detail['data']['questionSets'][0]['questions'][k1]['studentQA'][0]['stuAnswer'][0][
                        'mark'].strip()  # 我的答案
                    # 得分
                    score = work_detail["data"]['questionSets'][0]['questions'][k1]['studentQA'][0]['score']
                    count_str = str(count_)
                    f.write(
                        count_str + '.' + '[My_Answer]: ' + my_answer + '   [Myscore]:' + str(round(score, 2)))
                    if (k1+1) % 5 == 0:
                        f.write('\n')
                else:
                    count_str = str(count_)
                    f.write(count_str + '.' + '大题答案略!')
                f.write('\n')
                count_ += 1
            except:
                count_str = str(count_)
                f.write(count_str + '.' + '题目未作答或无答案!')
                f.write('\n')
                count_ += 1


def assist(homework_id, course_id_list, headers, Au):
    error_num = 0
    questions_id_list = []  # 存放所有问题的id
    work_detail_url = str(
        'https://cyber-tea-platform.anrunlu.net/stu/homework/' + str(course_id_list[homework_id]))
    homework_id1 = str(course_id_list[homework_id])
    work_detail = requests.get(url=work_detail_url, headers=headers).json()
    content = work_detail['data']['questionSets'][0]['questions'][0]['content']
    questions_num = get_qusetionnum(work_detail)
    for i in range(questions_num):
        try:
            # Question_id=data.questionSets[0].questions[0].id
            Question_id = work_detail['data']['questionSets'][0]['questions'][i]['id']
            questions_id_list.append(Question_id)  # 获取question_id

            # QuestionSet_id=data.questionSets[0]._id
            # 获取questionSet_id
            QuestionSet_id = work_detail["data"]['questionSets'][0]['_id']

            # 题目类型
            type_ = work_detail['data']['questionSets'][0]['questions'][i]['type']
            if type_ == '解答':  # 大题
                # 题目
                content = work_detail['data']['questionSets'][0]['questions'][i]['content']
                my_answer = work_detail['data']['questionSets'][0]['questions'][i]['studentQA'][0]['stuAnswer'][0][
                    'content'].strip()  # 我的答案
                # 得分
                score = work_detail["data"]['questionSets'][0]['questions'][i]['studentQA'][0]['score']
                if score == 0:  # 输出分数

                    print('[', type_, ']  ', '[', i + 1, ']', '.',
                          content.strip(), sep='', end='')  # 输出题干
                    print('(', my_answer, ')''  score: ', round(score, 2))
                    error_num += 1
            else:  # 选择和判断
                # 题目
                content = work_detail['data']['questionSets'][0]['questions'][i]['content']
                my_answer = work_detail['data']['questionSets'][0]['questions'][i]['studentQA'][0]['stuAnswer'][0][
                    'mark'].strip()  # 我的答案
                # 得分
                score = work_detail["data"]['questionSets'][0]['questions'][i]['studentQA'][0]['score']

                if score == 0:
                    print('[', type_, ']  ', '[', i + 1, ']', '.',
                          content.strip(), sep='', end='')  # 输出题干
                    print('(', my_answer, ')''  score: ', round(score, 2))
                    error_num += 1

            answer_chose_num = get_chiose_num(work_detail)
            if type_ == '解答' and score == 0:  # 输出解答题
                answer = work_detail['data']['questionSets'][0]['questions'][i]['answer'][0]['content'].strip(
                )
                mark = work_detail['data']['questionSets'][0]['questions'][i]['answer'][0]['mark'].strip(
                )
                print(mark + ': ' + answer, sep='', end='        ')
                print('\n', '-' * 60)
            elif type_ != '解答' and score == 0:  # 输出(非解答题选项)
                for j in range(answer_chose_num):  # 输出选项
                    answer = work_detail['data']['questionSets'][0]['questions'][i]['answer'][j]['content'].strip(
                    )
                    mark = work_detail['data']['questionSets'][0]['questions'][i]['answer'][j]['mark'].strip(
                    )
                    print(mark + ': ' + answer, sep='', end='        ')
                print('\n', '-' * 60)
        except:
            print(i, '题目未作答(无成绩)或出现错误')

            # 调用改错
    print('错题数量:', error_num)
    if error_num != 0:
        Correct_mistakes_chose = input('是否改错(Y/Any):')
        if Correct_mistakes_chose == 'Y':
            No = int(input('要修改的错题序号(上面输出的文本中使用[]括起来的是序号,输入-1退出改错):'))
            while No != -1:
                No -= 1
                # questions_id_list,QuestionSet_id,homework_id1 用于构件回答问题的post信息
                Correct(questions_id_list, QuestionSet_id, homework_id1, Au,
                        No)  # Correct只负责单个题改错,通过while控制是否继续改错,输入序号-1退出.
                # print('修改成功!')
                No = int(input('要修改的错题序号(上面输出的文本中使用[]括起来的是序号,输入-1退出改错):'))
        else:
            pass
    else:
        print('无错题,无需改错!\n')


def Correct(questions_id_list, QuestionSet_id, homework_id, Au, No):
    # Question_id=data.questionSets[0].questions[0].id
    # homework_id=str(course_id_list[homework_id]))
    # QuestionSet_id=data.questionSets[0]._id
    answer = input('输入选项(大写)(仅限选择)(输入其他内容返回上一级):')  # 仅限单选
    if answer == 'A' or answer == "B" or answer == "C" or answer == "D":
        post_answer(
            answer, Au, questions_id_list[No], QuestionSet_id, homework_id)
    else:
        print("请正确输入")


def post_answer(answer, Au, questions_id, questionset_id, homework_id):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
        'Authorization': Au,
        'Content-Type': 'application/json;charset=UTF-8'}
    answerforquestionURL = 'https://cyber-tea-platform.anrunlu.net/stu/question/answerForQuestion'  # 提交答案的URL
    # 构造请求头
    if answer == 'A':
        kwargs_A = {'homework_id': homework_id, 'questionSet_id': questionset_id, 'question_id': questions_id,
                    'stuAnswer': [{"mark": "A"}]}
        kwargs_A1 = json.dumps(kwargs_A)
        s = requests.post(url=answerforquestionURL,
                          headers=headers, data=kwargs_A1)
    elif answer == "B":
        kwargs_B = {'homework_id': homework_id, 'questionSet_id': questionset_id, 'question_id': questions_id,
                    'stuAnswer': [{"mark": "B"}]}
        kwargs_B1 = json.dumps(kwargs_B)
        s = requests.post(url=answerforquestionURL,
                          headers=headers, data=kwargs_B1)
    elif answer == "C":
        kwargs_C = {'homework_id': homework_id, 'questionSet_id': questionset_id, 'question_id': questions_id,
                    'stuAnswer': [{"mark": "C"}]}
        kwargs_C1 = json.dumps(kwargs_C)
        s = requests.post(url=answerforquestionURL,
                          headers=headers, data=kwargs_C1)
    elif answer == "D":
        kwargs_D = {'homework_id': homework_id, 'questionSet_id': questionset_id, 'question_id': questions_id,
                    'stuAnswer': [{"mark": "D"}]}
        kwargs_D1 = json.dumps(kwargs_D)
        s = requests.post(url=answerforquestionURL,
                          headers=headers, data=kwargs_D1)
    # print(s.json())
    if s.status_code == 201:
        print('修改成功,已将选项修改为', answer)
    else:
        print(s.json())

    print('\n')


if __name__ == "__main__":
    notendwork_count = 0
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0', }
    try:
        if not os.path.exists('Au.txt'):
            username = input('username:')
            password = input('password:')

            url_login = 'https://cyber-tea-platform.anrunlu.net/auth/login'
            login_args = {'password': password, 'username': username}

            r = requests.post(url=url_login, headers=headers, data=login_args)
            print(r.status_code)
            page = r.json()
            Authorization = page['data']['token']
            with open('Au.txt', mode='w') as f:
                f.write(Authorization)
        else:
            with open('Au.txt', mode='r') as f:
                Authorization = f.read()
        headers['Authorization'] = 'Bearer ' + str(Authorization)
        Au = 'Bearer ' + str(Authorization)
    except:
        print('密码错误!')
        time.sleep(3)
        sys.exit()
    course_url = 'https://cyber-tea-platform.anrunlu.net/stu/course'  # 获取课程列表
    course = requests.get(url=course_url, headers=headers)
    course = course.json()
    num = -1
    # print(course)
    for i in range(10):
        try:
            s = course['data'][i]
        except:
            num = i
        if num == i:
            break
    usr_url = 'https://cyber-tea-platform.anrunlu.net/auth/user'
    usr = requests.get(url=usr_url, headers=headers).json()
    usr_id = usr['data']['_id']
    a = usr_id[-1]
    try:
        a = int(a) + 1
    except:
        pass
    usr_id = usr_id[:-1] + str(a)  # 不知道为什么,这个id+1才是请求课程的id
    usr_name = usr['data']['nickname']
    print(usr_name)
    name_list = []
    ttc_id_list = []
    for i in range(num):
        name = course['data'][i]['course']['name']
        _id = course['data'][i]['_id']
        name_list.append(name)  # 获取所有课程的课程名
        ttc_id_list.append(_id)  # 获取所有课程的id

    work = ['课前预习', '课后作业', '课程实验', '课程论文', '课程设计', '毕业设计']

    filter_url = 'https://cyber-tea-platform.anrunlu.net/stu/homework/filter'  # 作业存储地的url

    home_work = []
    course_id_list = []
    count_ = 0
    work_isend = {}
    # 构造每一门课的请求头
    for i in range(num):
        print('-' * 60)
        print(name_list[i])
        count = 0
        for j in range(6):  # 这是一门课的六个作业种类

            kwargs = {'category': work[j],
                      'student_id': usr_id,
                      'tcc_id': ttc_id_list[i]}
            # 就地请求
            s = requests.post(url=filter_url, headers=headers, data=kwargs)
            s = s.json()
            home_work.append(s)  # homework里存放所有课程类别的json数据
            num = get_num(s)
            if num != 0:
                print(work[j])
            for k in range(num):
                count += 1
                print('题目序号: ', count_)
                d1, d2 = s['data'][k]['endtime'].split('T')
                d2, _ = d2.split(".")
                hours, minute, second = d2.split(':')  # 分割年月日
                year, month, day = d1.split('-')  # 分割小时分钟
                ss = list(map(int, [year, month, day, hours, minute, second]))
                a = datetime(ss[0], ss[1], ss[2], ss[3], ss[4], ss[5])
                a = a + timedelta(hours=8)
                now = datetime.today()
                print(count, ').', end="")
                print(s['data'][k]['title'], end=' ')
                if now > a:
                    print('已截止')
                else:
                    print('截至时间: ', a)
                    work_isend.setdefault(count_, s['data'][k]['id'])
                    notendwork_count += 1
                count_ += 1

                course_id = s['data'][k]['id']
                course_id_list.append(course_id)  # course_id_list配合输出的序号使用进入作业

    while True:

        print('-' * 30, '1.根据序号查看作业(无分数)', '-' * 30)
        print('-' * 30, '2.根据序号查看作业(有分数)', '-' * 30)
        print('-' * 30, '3.查看未完成作业', '-' * 30)
        print('-' * 30, '4.单个作业输出为错题本', '-' * 30)
        print('-' * 30, '5.批量将作业输出为错题本', '-' * 30)
        print('-' * 30, '6.辅助改错', '-' * 30)
        print('-' * 30, '0.退出程序', '-' * 30)
        # 查看作业,mode=1(无选项无评分)
        funcnum = int(input('选择功能:'))
        if funcnum == 1:
            homework_id = int(input('输入序号查看作业题目:'))
            show_homework(homework_id, course_id_list, headers)
            print()
        elif funcnum == 2:
            homework_id = int(input('输入序号查看作业题目:'))
            show_homework_(homework_id, course_id_list, headers)
            print()
        elif funcnum == 3:
            print('该功能所需时间较长,请耐心等待...')
            print('未截止作业数量:', notendwork_count)
            find_no_answer(work_isend, headers)
            print()

        elif funcnum == 4:
            n = int(input('题目序号:'))
            output_word(n, course_id_list, headers)
            print('输出完成!')
        elif funcnum == 5:  # 将单个作业输出
            try:
                many_n = list(map(int, input('输入多个序号按回车结束序号间用空格分分离:').split()))
                for n in many_n:
                    output_word(n, course_id_list, headers)
                print('输出完成!')
            except:
                print('出错了,请重试!')

        elif funcnum == 6:
            n = int(input('要改错的作业序号:'))
            assist(n, course_id_list, headers, Au)

        elif funcnum == 0:
            sys.exit()
