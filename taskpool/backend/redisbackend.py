from taskpool.data.task import Task, TaskContext
from taskpool.data.person import Person

class RedisBackend(object):
    def __init__(self, redis_server):
        self.redis_server = redis_server

    def get_task_by_id(self, task_id):
        return Task(task_id, self.__task_attr(task_id, "description"),
                    self.__task_attr(task_id, "state"), self.__task_attr(task_id, "context"))

    def __obj_attr(self, obj_name, obj_id, attr_name):
        return self.redis_server.get("%s:%s:%s" %(obj_name, obj_id, attr_name))

    def __context_attr(self, context_id, attr_name):
        return self.__obj_attr("context", context_id, attr_name)

    def __task_attr(self, task_id, attr_name):
        return self.__obj_attr("task", task_id, attr_name)
    
    def get_context_by_id(self, context_id):
        return TaskContext(context_id, self.__context_attr(context_id, "name"))

    def new_task(self, person_id, task_description, context):
        r = self.redis_server
        task_id = int(r.incr("next.task.id"))
        r.sadd("tasks", task_id)
        r.set("task:%s:description" %task_id, task_description)
        task = Task(task_id, task_description, "", context)
        r.rpush("person:%s:tasks" %person_id, task_id)
        return task

    def new_person(self, person_name):
        r = self.redis_server
        person_id = int(r.incr("next.person.id"))
        r.set("person:%s:name" %person_id, person_name)
        r.sadd("persons", person_id)
        return Person(person_id, person_name, [])

    def all_contexts(self):
        r = self.redis_server
        context_ids = [int(i) for i in r.smembers("contexts")]
        return dict([(cid, self.get_context_by_id(cid)) for cid in context_ids])
