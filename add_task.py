import webapp2
import jinja2
import os
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User
from task_board import TasksBoard
from task import Task

from helpers import getTaskBoardList, getUserList, getTaskBoardMembers, getProspectiveMembersList, getFormattedDateInstance, isATaskBoardMember

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), 'views')),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class AddTaskToTaskBoardPage(webapp2.RequestHandler):
    def get(self, selected_task_board_id):
        self.response.headers['Content-Type'] = 'text/html'
        url = ''
        my_user = None
        user = users.get_current_user()
        should_update_account = False
        user_fullname = ''
        has_error = False
        id = ''
        task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()
        task_name = ''
        msg = ''
        due_date = ''

        try:
            if 'task_name' in self.request.GET or 'msg' in self.request.GET:
                has_error = True
                task_name = '' if self.request.get('task_name') == None else self.request.get('task_name')
                due_date = '' if self.request.get('due_date') == None else self.request.get('due_date')
                msg = '' if self.request.get('msg') == None else self.request.get('msg')
        except:
            pass

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        else:
            url = users.create_logout_url( self.request.uri )
            my_user_key = ndb.Key('User', user.user_id())
            my_user = my_user_key.get()

            if my_user:
                if my_user.lastname and my_user.othernames:
                    should_update_account = False
                    user_fullname = my_user.othernames + " " + my_user.lastname

        if not isATaskBoardMember(task_board, str(my_user.key.id())):
            self.redirect('/?msg=You do not have access to ' + task_board.name + ' task board')

        template_values = {
            'url': url,
            'user': user,
            'should_update_account': should_update_account,
            'user_fullname': user_fullname,
            'has_error': has_error,
            'msg': msg,
            'id': id,
            'task_board': task_board,
            'selected_task_board_id': selected_task_board_id,
            'task_name': task_name,
            'due_date': due_date
        }

        template = JINJA_ENVIRONMENT.get_template('add_task_to_task_board.html')
        self.response.write(template.render(template_values))
        return

    def post(self, selected_task_board_id):
        self.response.headers['Content-Type'] = 'text/html'
        selected_task_board_id = selected_task_board_id
        task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()

        task_name = self.request.get('task_name')
        due_date = self.request.get('due_date')

        if task_name == '' or due_date == '':
            self.redirect('/' + selected_task_board_id + '/add-task-to-task-board?task_name=' + task_name + '&due_date=' + due_date )
            return
        else:
            can_add_task = True
            for task in task_board.board_tasks:
                if task.title.lower() == task_name.lower():
                    can_add_task = False

            if can_add_task:
                title = task_name
                due_date = getFormattedDateInstance(due_date)
                completed = False
                completed_on = None
                is_assigned = False
                assigned_to = ''
                new_task = Task(title=title, due_date=due_date, completed=completed, completed_on=completed_on, is_assigned=is_assigned, assigned_to=assigned_to, marked_as_unassigned=False)
                task_board.board_tasks.append(new_task)
                task_board.put()
                self.redirect('/' + selected_task_board_id )
                return
            else:
                message = 'Task title already exist on task board'
                self.redirect('/' + selected_task_board_id + '/add-task-to-task-board?msg=' + message + '&task_name=' + task_name + '&due_date=' + due_date )
                return
