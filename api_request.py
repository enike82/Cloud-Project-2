import webapp2
import jinja2
import os
import datetime
import json

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User
from task_board import TasksBoard
from task import Task


from helpers import getTaskBoardList, getUserList, getTaskBoardMembers, getProspectiveMembersList, getFormattedDateInstance, isATaskBoardMember

class APIPOSTRequestHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json'
        user = users.get_current_user()
        my_user_key = ndb.Key('User', user.user_id())
        my_user = my_user_key.get()
        data = self.request.body
        response_dict = {}

        request_list = data.split('&')
        action = request_list[len(request_list) - 1].split('=')[1]

        if len(request_list) == 4 and action == "assign-task-to-member":
            task_board_id = int(request_list[0].split('=')[1])
            task_index = int(request_list[1].split('=')[1])
            board_member_id = request_list[2].split('=')[1]

            task_board = ndb.Key('TasksBoard', task_board_id).get()
            if not isATaskBoardMember(task_board, str(my_user.key.id())):
                response_dict['code'] = 400
                message = 'You do not have access to ' + task_board.name + ' task board'
                response_dict['message'] = message
                response_dict['url'] = '/?msg=' + message
                self.response.write( json.dumps( response_dict ) )
                return

            if board_member_id:
                task_board.board_tasks[task_index].is_assigned = True
                task_board.board_tasks[task_index].marked_as_unassigned=False
            else:
                task_board.board_tasks[task_index].is_assigned = False

            task_board.board_tasks[task_index].assigned_to = board_member_id
            task_board.put()
            response_dict['board'] = task_board.board_tasks[task_index].assigned_to
            response_dict['code'] = 200
            response_dict['message'] = 'Task assigned to a board member successfully'
        elif len(request_list) == 4 and action == "update-checked-task-status":
            task_board_id = int(request_list[0].split('=')[1])
            task_index = int(request_list[1].split('=')[1])
            completed = request_list[2].split('=')[1].capitalize()
            completed_on = datetime.datetime.now()

            task_board = ndb.Key('TasksBoard', task_board_id).get()
            if not isATaskBoardMember(task_board, str(my_user.key.id())):
                response_dict['code'] = 400
                message = 'You do not have access to ' + task_board.name + ' task board'
                response_dict['message'] = message
                response_dict['url'] = '/?msg=' + message
                self.response.write( json.dumps( response_dict ) )
                return

            if completed == 'True':
                task_board.board_tasks[task_index].completed = True
                task_board.board_tasks[task_index].completed_on = completed_on
            else:
                task_board.board_tasks[task_index].completed = False
                task_board.board_tasks[task_index].completed_on = None
            task_board.put()
            response_dict['code'] = 200
            response_dict['message'] = 'Task completed status updated successful'
        self.response.write( json.dumps( response_dict ) )
        return
        
