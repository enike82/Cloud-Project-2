import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from task_board import TasksBoard
from helpers import isATaskBoardMember, getUserList

class DeleteTaskBoardPage(webapp2.RequestHandler):
    def get(self, selected_task_board_id):
        task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) )
        task_board_name = task_board.get().name
        task_board.delete()
        user_list = getUserList()
        for user in user_list:
            for board_key in user.user_boards:
                if board_key == selected_task_board_id:
                    user.user_boards.remove(board_key)
                    user.put()
        self.redirect('/?msg=' + task_board_name + ' task board was successfully deleted.')
        return
