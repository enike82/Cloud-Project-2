import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User
from task_board import TasksBoard

from helpers import getTaskBoardList, getUserList, getTaskBoardMembers, getProspectiveMembersList, isATaskBoardMember, getUserByKey

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), 'views')),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class InviteMemberToTaskBoardPage(webapp2.RequestHandler):
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
        selected_member_id = None

        try:
            if 'selected_member_id' in self.request.GET:
                has_error = True
                selected_member_id = self.request.get('selected_member_id')
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

        prospective_member_list = getProspectiveMembersList(getUserList(), task_board)
        template_values = {
            'url': url,
            'user': user,
            'should_update_account': should_update_account,
            'user_fullname': user_fullname,
            'has_error': has_error,
            'msg': msg,
            'id': id,
            'task_board': task_board,
            'prospective_member_list': prospective_member_list,
            'selected_task_board_id': selected_task_board_id,
            'selected_member_id': selected_member_id
        }

        template = JINJA_ENVIRONMENT.get_template('invite_board_member_to_task_board.html')
        self.response.write(template.render(template_values))
        return

    def post(self, selected_task_board_id):
        self.response.headers['Content-Type'] = 'text/html'
        selected_task_board_id = selected_task_board_id

        selected_member_id = self.request.get('member_id')
        if selected_member_id == '':
            self.redirect('/' + selected_task_board_id + '/add-task-board-member?selected_member_id=' + selected_member_id )
            return
        else:
            task_board = ndb.Key( 'TasksBoard', int(selected_task_board_id) ).get()
            task_board.board_members.append(selected_member_id)
            invited_user = getUserByKey(getUserList(), selected_member_id)
            k = task_board.put()
            invited_user.user_boards.append(str(k.get().key.id()))
            invited_user.put()
            self.redirect('/' + selected_task_board_id )
            return
