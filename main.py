import webapp2
import jinja2
import os

import logging

from google.appengine.api import users
from google.appengine.ext import ndb

class Player(ndb.Model):
    name = ndb.StringProperty()
    score = ndb.IntegerProperty()

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class LoginPage(webapp2.RequestHandler):
    def get(self):

        template = env.get_template('templates/login.html')
        self.response.write(template.render())

    def post(self):
        name = self.request.get('name')
        #get everyone from the database
        players = Player.query().fetch()

        #if the player doesn't have a created name in the database make one
        current_player = Player.query().filter(Player.name == name).get()
        if current_player == None:
            current_player = Player(name = name, score = 0)
            current_player.put()

        #send the link of their key over the url
        urlsafe_key = current_player.key.urlsafe()

        self.redirect('/game?key=' + urlsafe_key)

class GamePage(webapp2.RequestHandler):
    def get(self):
        #1 Read the database
        #Fetch the entire list of players
        players = Player.query().order(-Player.score).fetch()
        #Get key from URL to find the actual player
        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        current_player = key.get()

        templateVars = {
            'players' : players,
            'current_player' : current_player,
        }

        template = env.get_template('templates/game.html')
        self.response.write(template.render(templateVars))

    def post(self):
        players = Player.query().order(-Player.score).fetch()

        urlsafe_key = self.request.get('key')
        key = ndb.Key(urlsafe = urlsafe_key)
        current_player = key.get()

        current_player.score += 1
        current_player.put()

        templateVars = {
            'players' : players,
            'current_player' : current_player,
        }

        template = env.get_template('templates/game.html')
        self.response.write(template.render(templateVars))

app = webapp2.WSGIApplication([
    ('/', LoginPage),
    ('/game', GamePage),
], debug=True)


#INTERACTIVE CONSOLE
# patches_query = Patch.query()
# patches_query = Patch.query().filter(Patch.inner_color == "blue") <-- filter + order oldest to newest
#patches_query = patches_query.order(-Patch.created_time) <--- normally oldest to newest, - for reverse
# first_patch = patches_query.get() #gets one
#
# patches = patches_query.fetch() #gets all the data, ORDER before fetching
# first_patch.inner_color = "lightblue"
# first_patch.put() <--- saves it into the database
# first_patch.key.delete() <--- key is like SSN

#CRUD - Create(call the class and then save with .put()), Read(get, fetch), Update(.put), Delete(.key.delete)
