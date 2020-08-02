import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User
from task_board import TasksBoard

from helpers import isATaskBoardMember

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), 'views')),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class EditTaskBoardPage(webapp2.RequestHandler):
    def get(self, selected_task_board_id):
        self.response.headers['Content-Type'] = 'text/html'
        url = ''
        my_user = None
        user = users.get_current_user()
        should_update_account = False
        user_fullname = ''
        has_error = False
        task_board_name = ''
        task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()

        try:
            if 'task_board_name' in self.request.GET:
                has_error = True
                task_board_name = '' if self.request.get('task_board_name') == None else self.request.get('task_board_name')
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
            else:
                self.redirect('/update-account')
                return

        if not isATaskBoardMember(task_board, str(my_user.key.id())):
            self.redirect('/?msg=You do not have access to ' + task_board.name + ' task board')

        template_values = {
            'url': url,
            'user': user,
            'should_update_account': should_update_account,
            'has_error': has_error,
            'task_board_name': task_board_name,
            'user_fullname': user_fullname,
            'task_board': task_board
        }

        template = JINJA_ENVIRONMENT.get_template('edit_task_board.html')
        self.response.write(template.render(template_values))
        return

    def post(self, selected_task_board_id):
        self.response.headers['Content-Type'] = 'text/html'

        if self.request.get('task_board_name') == '':
            task_board_name = '' if self.request.get('task_board_name') == None else self.request.get('task_board_name')
            self.redirect('/' + selected_task_board_id + '/edit-task-board?task_board_name=' + task_board_name)
            return
        else:
            name = self.request.get('task_board_name')
            task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()
            task_board.name = name
            task_board.put()
            self.redirect('/')
            return
