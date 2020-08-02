import webapp2
import jinja2
import os

from datetime import datetime
import pytz

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User
from task_board import TasksBoard

from helpers import getTaskBoardList, getUserList, getTaskBoardMembers, isATaskBoardMember, getActiveTasks, getCompletedTasks, getTaskCompletedToday

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), 'views')),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class SelectedTaskBoardPage(webapp2.RequestHandler):
    def get(self, selected_task_board_id):
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
            'task_board_id': selected_task_board_id,
            'task_board': task_board,
            'board_members': getTaskBoardMembers(getUserList(), task_board.board_members),
            'total_task': len(task_board.board_tasks),
            'active_task': getActiveTasks(task_board.board_tasks),
            'completed_task': getCompletedTasks(task_board.board_tasks),
            'task_completed_today': getTaskCompletedToday(task_board.board_tasks),
            'dateTimeConvert': self.dateTimeConvert
        }

        template = JINJA_ENVIRONMENT.get_template('selected_task_board.html')
        self.response.write(template.render(template_values))
        return

    def dateTimeConvert(self, date_time_instance):
        target_tz = pytz.timezone("Europe/Dublin")
        return datetime.strptime(str(date_time_instance), '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=pytz.utc).astimezone(target_tz)
