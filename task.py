from google.appengine.ext import ndb

class Task(ndb.Model):
    title = ndb.StringProperty()
    due_date = ndb.DateProperty()
    completed = ndb.BooleanProperty()
    completed_on = ndb.DateTimeProperty()
    is_assigned = ndb.BooleanProperty()
    assigned_to = ndb.StringProperty()
    marked_as_unassigned = ndb.BooleanProperty()
