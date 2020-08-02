from google.appengine.ext import ndb

from user import User
from task_board import TasksBoard

import datetime

from datetime import datetime as format_datetime

def getTaskBoardList(user_board_list):
    board_list = []
    for board_id in user_board_list:
        task_board = ndb.Key( 'TasksBoard', int(board_id) ).get()
        board_list.append(task_board)
    return board_list

def getUserList():
    return User.query().fetch()

def getUserByKey(user_list, user_key):
    user = None
    for temp_user in user_list:
        if str(temp_user.key.id()) == user_key:
            user = temp_user
    return user

def getTaskBoardMembers(user_list, task_board_members):
    board_members = []

    for board_member_id in task_board_members:
        for board_member in user_list:
            if board_member_id == str(board_member.key.id()):
                board_members.append(board_member)

    return board_members

def getProspectiveMembersList(user_list, task_board):
    prospective_members_list = []

    for user in user_list:
        is_a_prospect = True
        for user_id in task_board.board_members:
            print(user_id)
            print(str(user.key.id()))
            if user_id == str(user.key.id()):
                is_a_prospect = False

        if is_a_prospect:
            prospective_members_list.append(user)

    return prospective_members_list

def getFormattedDateInstance(date_string):
    return format_datetime.strptime(str(date_string), '%Y-%m-%d').date()

def isATaskBoardMember(task_board, member_id):
    task_board_member = False
    for member in task_board.board_members:
        if member == member_id:
            task_board_member = True
    return task_board_member

def getActiveTasks(task_list):
    count = 0
    for task in task_list:
        if not task.completed:
            count += 1
    return count

def getCompletedTasks(task_list):
    count = 0
    for task in task_list:
        if task.completed:
            count += 1
    return count

def getTaskCompletedToday(task_list):
    count = 0
    for task in task_list:
        if task.completed and task.completed_on.strftime('%Y-%m-%d') == datetime.datetime.now().strftime('%Y-%m-%d'):
            count += 1
    return count
