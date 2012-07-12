class Task(object):
    def __init__(self, task_id, description, state, context, persons = []):
        self.__id = task_id
        self.__desc = description
        self.__state = state
        self.__context = context
        self.persons = list(persons) # TODO add relation

    @property
    def task_id(self):
        return self.__id

    @property
    def description(self):
        return self.__desc

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        # TODY verify value is one of the predefined states
        self.__state = value

    @property
    def context(self):
        return self.__context

    @context.setter
    def context(self, value):
        # TODY verify value is one of the predefined contexts
        self.__context = value

    def __repr__(self):
        return "Task(%s, %s, %s, %s, %s)" %(self.task_id, self.description, self.state, self.context, self.persons)
    
    def __unicode__(self):
        return u'%s' %self.description

class TaskContext(object):
    def __init__(self, context_id, name):
        self.context_id = context_id
        self.name = name

    def __repr__(self):
        return "TaskContext(%s, %s)" %(self.context_id, self.name)
    
    def __unicode__(self):
        return self.name
