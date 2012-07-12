from jinja2 import Environment, FileSystemLoader
from taskpool.backend.redisbackend import RedisBackend
from taskpool.data.person import Person
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.utils import redirect
from werkzeug.wrappers import Request, Response
import os

default_contexts = {1: {"name": "office"},
                    2: {"name": "phone"},
                    3: {"name": "home"},
                    4: {"name": "outside"}}

# TODO try converting to flask http://flask.pocoo.org/docs/quickstart/

class Server(object):

    def __init__(self, config):
        self.redis = config['backend']
        self.backend = RedisBackend(self.redis)
        self.init_templating()
        self.add_routing()
        self.init_contexts()
        self.read_data()

    def init_contexts(self):
        r = self.redis
        self.contexts = self.backend.all_contexts()
        print ("context before:", self.contexts)
        if not self.contexts:
            for (context_id, context_attribs) in default_contexts.items():
                r.sadd("contexts", context_id)
                for attr_name,attr_val in context_attribs.items():
                    r.set("context:%s:%s" %(context_id, attr_name), attr_val)
        self.contexts = self.backend.all_contexts()
        print ("context after:", self.contexts)

    def read_data(self):
        r = self.redis
        person_ids = [int(i) for i in r.smembers("persons")]
        if len(person_ids) == 0:
            r.set("next.person.id", 0)
        self.persons = {}
        self.tasks = {}
        for person_id in person_ids:
            name = r.get("person:%s:name" %person_id)
            task_ids = [int(i) for i in r.lrange("person:%s:tasks" %person_id, 0, -1)]
            person_tasks = []
            for task_id in task_ids:
                if task_id not in self.tasks:
                    task = self.backend.get_task_by_id(task_id)
                else:
                    task = self.tasks[task_id]
                person_tasks.append(task)
            person = Person(person_id, name, person_tasks)
            self.persons[person_id] = person

    def init_templating(self):
        template_path = os.path.join(os.path.dirname(__file__), '../../templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)

    def add_routing(self):
        self.url_map = Map([
            Rule('/', endpoint='homepage'),
            Rule('/persons/register', endpoint='register_form'),
            Rule('/persons/new', endpoint='register_submit'),
            Rule('/new/<int:person_id>', endpoint='new_task'),
            Rule('/persons', endpoint='person_list'),
            Rule('/person/<int:person_id>', endpoint='person_tasks'),
            #Rule('/<short_id>+', endpoint='short_link_details')
        ])

    def on_register_submit(self, request):
        person_name = request.form['person_name']
        person = self.backend.new_person(person_name)
        person_id = person.person_id
        self.persons[person_id] = person
        return redirect('/person/%s' %person_id)

    def on_register_form(self, request):
        return self.render_template("register.html")

    def on_homepage(self, request):
        return self.render_template("welcome.html", persons=self.persons.values())

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except HTTPException, e:
            return e

    def on_new_task(self, request, person_id):
        if person_id not in self.persons:
            return self.error("No person with id " + person_id)
        task_description = request.form["task_description"]
        context_id = int(request.form['context'])
        context = self.contexts[context_id] if context_id in self.contexts else None
        print "id: %s context: %s" %(context_id, context) 
        task = self.backend.new_task(person_id, task_description, context)
        self.persons[person_id].add_task(task)
        return redirect('/person/%s' %person_id)

    def on_person_list(self, request):
        return self.render_template("person_list.html", persons=self.persons.values())

    def error(self, error_message):
        return self.render_template("error.html", error=error_message)

    def on_person_tasks(self, request, person_id):
        if person_id not in self.persons:
            return self.error("No person with id %s" %person_id)
        person = self.persons[person_id]
        return self.render_template("person_tasks.html", person=person, tasks=person.tasks, 
                                    contexts=self.contexts.values())

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        print "Env: %s" %environ
        print "request: %s" %request
        print "response: %s" %response
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
