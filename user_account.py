import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from user import User

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.join( os.path.dirname(__file__), 'views')),
    extensions = [ 'jinja2.ext.autoescape' ],
    autoescape = True
)

class UserAccountPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        user = users.get_current_user()
        should_update_account = True
        lastname = ''
        othernames = ''
        has_error = False

        try:
            if 'lastname' in self.request.GET or 'othernames' in self.request.GET:
                has_error = True
                lastname = '' if self.request.get('lastname') == None else self.request.get('lastname')
                othernames = '' if self.request.get('othernames') == None else self.request.get('othernames')
        except:
            pass

        template_values = {
            'user': user,
            'should_update_account': should_update_account,
            'has_error': has_error,
            'lastname': lastname,
            'othernames': othernames
        }

        template = JINJA_ENVIRONMENT.get_template('account.html')
        self.response.write(template.render(template_values))
        return

    def post(self):
        self.response.headers['Content-Type'] = 'text/html'

        if self.request.get('lastname') == '' or self.request.get('othernames') == '':
            lastname = '' if self.request.get('lastname') == None else self.request.get('lastname')
            othernames = '' if self.request.get('othernames') == None else self.request.get('othernames')
            self.redirect('/update-account?lastname=' + lastname + '&othernames=' + othernames)
            return
        else:
            user = users.get_current_user()
            my_user_key = ndb.Key( 'User', user.user_id() )
            my_user = my_user_key.get()
            my_user.lastname = self.request.get('lastname')
            my_user.othernames = self.request.get('othernames')
            my_user.email = user.email()
            my_user.put()
            self.redirect('/')
            return
