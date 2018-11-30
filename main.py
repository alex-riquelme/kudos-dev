from google.appengine.api import users
import webapp2
from google.appengine.ext import ndb
import time
import datetime as dt
#import cloudstorage as gcs
#from google.appengine.api import app_identity

class Users(ndb.Model):
    mail = ndb.StringProperty()
    admin = ndb.BooleanProperty()
    company = ndb.StringProperty()
    name = ndb.StringProperty()
    photo = ndb.StringProperty()
    shard = ndb.StringProperty()
    work_position = ndb.StringProperty()
    kudos = ndb.IntegerProperty()
    points = ndb.IntegerProperty()
   
   
class Transaction_kudos(ndb.Model):
    admin_comment = ndb.StringProperty()
    comment = ndb.StringProperty()
    quantity_kudos = ndb.IntegerProperty()
    receiver = ndb.StringProperty()
    sender = ndb.StringProperty()
    timestamp = ndb.StringProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        # [START user_details]
        
        
        
        user = users.get_current_user()
        
        # This "if" is to verify if  the user is logged in or not      
        if user:
            mail = user.nickname()
            username = mail.split("@")[0]
            ancestor_key = ndb.Key('Users', username)
            user_entity = ancestor_key.get()

            # This "if" verify if the users exists in datastore            
            if user_entity:
                # Get photo from bucket
                #bucket_name = os.environ.get('kudos-users', app_identity.get_default_gcs_bucket_name())
                #bucket = '/' + bucket_name
                #filename= bucket + '/' + user_entity.photo()
                #gcs_file = gcs.open(filename)
                #contents = gcs_file.read()
                contents=""
                #gcs_file.close()
   

                #user_entity = User.query(ancestor=ancestor_key).get()
                logout_url = users.create_logout_url('/')

                greeting = '<img src="{}" />Welcome, {}, here you have your kudos: {}! (<a href="{}">sign out</a>)<br/><br/> <form action="/sendKudos">User:<br><input type="text" name="receiver" placeholder="jhondoe"><br/>kudos:<br><select name="kudos"><option value=2>2</option><option value=10>10</option><option value=20>20</option><option value=30>30</option><option value=40>40</option><option value=50>50</option></select><br/><textarea name="comment" placeholder="Enter text here..."></textarea><br/><input type="submit" value="Send kudos"></form>'.format(contents,mail,user_entity.kudos,logout_url)
                
            else:
                greeting = '<html><body>You are not a member of the team.</body></html>'
            
        else:
            login_url = users.create_login_url('/')
            greeting = '<a href="{}">Sign in</a>'.format(login_url)
        # [END user_details]
     
        self.response.write(
            '<html><body>{}</body></html>'.format(greeting))


class AdminPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.response.write('You are an administrator.')
            else:
                self.response.write('You are not an administrator.')
        else:
            self.response.write('You are not logged in.')

class sendKudos(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            mail = user.nickname()
            username = mail.split("@")[0]
            ancestor_key = ndb.Key('Users', username)
            user_entity = ancestor_key.get()

            # This "if" verify if the users exists in datastore            
            if user_entity:
                
                # Get parameters from url
                receiver = self.request.get_all("receiver")
                kudos = self.request.get_all("kudos")
                comment = self.request.get_all("comment")
                # Decode from utf8
                receiver = receiver[0].decode('utf8')
                kudos = kudos[0].decode('utf8')
                comment = comment[0].decode('utf8')
                
                # consult if the receiver really exists in datastore
                receiver_ancestor_key = ndb.Key('Users', receiver)
                receiver_entity = receiver_ancestor_key.get()
                if receiver_entity:
                    if kudos == "2" or kudos == "10" or kudos == "20" or kudos == "30" or kudos == "40" or kudos == "50":
                        # Adding the points to receiver
                        receiver_entity.points = receiver_entity.points + int(kudos)
                        receiver_entity.put()
                
                        # Substracting the points to the sender
                        user_entity.kudos = user_entity.kudos - int(kudos)
                        user_entity.put()
                
                        # Adding Comment into Datastore
                        epoch_now = time.time()
                        frmt_date = dt.datetime.utcfromtimestamp(epoch_now).strftime("%Y-%m-%d (%H:%M:%S.%f")[:-3]
                        frmt_date = frmt_date + ") CET"
                
                        kudos_trans = Transaction_kudos(admin_comment='', comment=comment, quantity_kudos=int(kudos), receiver=receiver, sender=username, timestamp=frmt_date)
                        kudos_trans.put()
                        # Transaction done.
                        self.response.write('{} Kudos sent to {}. <br/>Comment: <br/>{}'.format(kudos,receiver,comment))
                    else:
                        self.response.write("<html><body>It's not possible to send that amount of kudos.</body></html>")
                else:
                    self.response.write("<html><body>The user doesn't exists.</body></html>")
            else:
                self.response.write('<html><body>You are not a member of the team.</body></html>')
        else:
            self.response.write('You are not logged in.')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/admin', AdminPage),
    ('/sendKudos', sendKudos)
], debug=True)
