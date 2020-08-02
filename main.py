import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User
from task_board import TasksBoard
from user_account import UserAccountPage
from create_task_board import CreateTaskBoardPage
from selected_task_board import SelectedTaskBoardPage
from invite_board_member import InviteMemberToTaskBoardPage
from api_request import APIPOSTRequestHandler
from add_task import AddTaskToTaskBoardPage
from edit_task import EditTaskPage
from delete_task import DeleteTaskPage
from edit_task_board import EditTaskBoardPage
from delete_member import DeleteMemberPage
from delete_task_board import DeleteTaskBoardPage

from helpers import getTaskBoardList, getUserList

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), 'views')),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        url = ''
        my_user = None
        user = users.get_current_user()
        should_update_account = False
        user_fullname = ''
        has_error = False
        msg = ''
        id = ''
        task_boards = None

        try:
            if 'msg' in self.request.GET or 'id' in self.request.GET:
                has_error = True
                msg = self.request.get('msg')
                id = self.request.get('id')
        except:
            pass

        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        else:
            url = users.create_logout_url( self.request.uri )
            my_user_key = ndb.Key('User', user.user_id())
            my_user = my_user_key.get()

            if my_user == None:
                my_user = User(id=user.user_id())
                my_user.put()
                self.redirect('/update-account')
                return
            else:
                if my_user.lastname and my_user.othernames:
                    should_update_account = False
                    user_fullname = my_user.othernames + " " + my_user.lastname
                else:
                    self.redirect('/update-account')
                    return

        task_boards = getTaskBoardList(my_user.user_boards)

        template_values = {
            'url': url,
            'user': user,
            'should_update_account': should_update_account,
            'user_fullname': user_fullname,
            'has_error': has_error,
            'msg': msg,
            'id': id,
            'task_boards': task_boards,
            'task_board_length': len(task_boards)
        }

        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_values))
        return

app = webapp2.WSGIApplication([
    webapp2.Route(r'/', handler=MainPage),
    webapp2.Route(r'/create-task-board', handler= CreateTaskBoardPage),
    webapp2.Route(r'/post-api-services', handler=APIPOSTRequestHandler),
    webapp2.Route(r'/update-account', handler=UserAccountPage),
    webapp2.Route(r'/<selected_task_board_id:[^/]+>', handler=SelectedTaskBoardPage),
    webapp2.Route(r'/<selected_task_board_id:[^/]+>/add-task-board-member', handler=InviteMemberToTaskBoardPage),
    webapp2.Route(r'/<selected_task_board_id:[^/]+>/add-task-to-task-board', handler=AddTaskToTaskBoardPage),
    webapp2.Route(r'/<selected_task_board_id:[^/]+>/delete-task-board', handler=DeleteTaskBoardPage),
    webapp2.Route(r'/<selected_task_board_id:[^/]+>/edit-task-board', handler=EditTaskBoardPage),
    webapp2.Route(r'/<selected_task_board_id:[^/]+>/members/<member_id:[^/]+>/delete-member', handler=DeleteMemberPage),
    webapp2.Route(r'/<selected_task_board_id:[^/]+>/tasks/<task_index:[^/]+>/edit-task', handler=EditTaskPage),
    webapp2.Route(r'/<selected_task_board_id:[^/]+>/tasks/<task_index:[^/]+>/delete-task', handler=DeleteTaskPage),
], debug = True)
