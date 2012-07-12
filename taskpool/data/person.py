class Person(object):
    def __init__(self, person_id, name, tasks):
        self.__id = person_id
        self.__name = name
        self.tasks = list(tasks)

    @property
    def person_id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def n_tasks(self):
        return len(self.tasks)

    def add_task(self, task):
        self.tasks.append(task)
    
    def remove_task(self, task):
        if task in self.tasks:
            self.tasks.remove(task)

    def __repr__(self):
        return "Person(%s, %s, %s)"  %(self.person_id, self.name, self.tasks)

    def __unicode(self):
        return u'%s' %self.__name
