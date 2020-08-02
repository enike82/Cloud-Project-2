import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from task_board import TasksBoard
from helpers import isATaskBoardMember, getUserByKey, getUserList

class DeleteMemberPage(webapp2.RequestHandler):
    def get(self, selected_task_board_id, member_id):
        user = users.get_current_user()
        my_user_key = ndb.Key('User', user.user_id())
        my_user = my_user_key.get()

        task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()

        if not isATaskBoardMember(task_board, str(my_user.key.id())):
            self.redirect('/?msg=You do not have access to ' + task_board.name + ' task board')

        for task in task_board.board_tasks:
            if task.assigned_to == member_id:
                task.assigned_to = ''
                task.is_assigned = False
                task.completed = False
                task.completed_on = None
                task.marked_as_unassigned = True

        task_board.board_members.remove(member_id)
        invited_user = getUserByKey(getUserList(), member_id)
        k = task_board.put()
        invited_user.user_boards.remove(str(k.get().key.id()))
        invited_user.put()
        self.redirect("/" + str(task_board.key.id()) )
        return
