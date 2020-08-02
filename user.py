from google.appengine.ext import ndb

class User(ndb.Model):
    lastname = ndb.StringProperty()
    othernames = ndb.StringProperty()
    email = ndb.StringProperty()
    user_boards = ndb.StringProperty(repeated = True)
