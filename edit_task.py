import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User
from task_board import TasksBoard

from helpers import getTaskBoardList, getUserList, getTaskBoardMembers, getFormattedDateInstance, isATaskBoardMember

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), 'views')),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class EditTaskPage(webapp2.RequestHandler):
    def get(self, selected_task_board_id, task_index):
        self.response.headers['Content-Type'] = 'text/html'
        url = ''
        my_user = None
        user = users.get_current_user()
        should_update_account = False
        user_fullname = ''
        has_error = False
        msg = ''
        id = ''
        task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()
        task = task_board.board_tasks[int(task_index)]
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
            'task_name': task_name,
            'due_date': due_date,
            'task_board_id': selected_task_board_id,
            'task_board': task_board,
            'board_members': getTaskBoardMembers(getUserList(), task_board.board_members),
            'task': task,
            'task_index': task_index
        }

        template = JINJA_ENVIRONMENT.get_template('edit_task_on_task_board.html')
        self.response.write(template.render(template_values))
        return

    def post(self, selected_task_board_id, task_index):
        self.response.headers['Content-Type'] = 'text/html'
        selected_task_board_id = selected_task_board_id
        task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()

        task_name = self.request.get('task_name')
        due_date = self.request.get('due_date')

        if task_name == '' or due_date == '':
            self.redirect('/' + selected_task_board_id + '/tasks/' + task_index + '/edit-task?task_name=' + task_name + '&due_date=' + due_date )
            return
        else:
            task_board = ndb.Key('TasksBoard', int(selected_task_board_id)).get()
            task_board.board_tasks[int(task_index)].title = task_name
            task_board.board_tasks[int(task_index)].due_date = getFormattedDateInstance(due_date)
            task_board.put()
            self.redirect('/' + selected_task_board_id )
            return
