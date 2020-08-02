import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from task_board import TasksBoard
from helpers import isATaskBoardMember

class DeleteTaskPage(webapp2.RequestHandler):
    def get(self, selected_task_board_id, task_index):
        user = users.get_current_user()
        my_user_key = ndb.Key('User', user.user_id())
        my_user = my_user_key.get()

        task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()

        if not isATaskBoardMember(task_board, str(my_user.key.id())):
            self.redirect('/?msg=You do not have access to ' + task_board.name + ' task board')

        task_board.board_tasks.remove(task_board.board_tasks[int(task_index)])
        task_board.put()
        self.redirect("/" + str(task_board.key.id()) )
        return
        
