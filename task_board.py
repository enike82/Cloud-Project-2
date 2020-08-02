from google.appengine.ext import ndb
from task import Task

class TasksBoard(ndb.Model):
    name = ndb.StringProperty()
    created_by = ndb.StringProperty()
    board_members = ndb.StringProperty(repeated = True)
    board_tasks = ndb.StructuredProperty(Task, repeated = True)
