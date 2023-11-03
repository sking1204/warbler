"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

from flask import session

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

#Test case class: MessageViewTestCase - inherits from 'TestCase'
#('TestCase is a common base class provided by testing frameworks to 
# create test cases)


class MessageViewTestCase(TestCase):
    """Test views for messages."""

#the 'setUp' method is called before each test method within the test case
#(used to set up any necessary preconditions for the tests)

    def setUp(self):
        """Create test client, add sample data."""

#User.query.delete -> this will delete all records from the 'User' model.
#This is to ensure a clean and predictable state for the test.

        User.query.delete()

#Message.query.delete -> this will delete all records from the "Message" model.
#This is to ensure a clean and predictable state for the test.

        Message.query.delete()

#'self.client=app.test_client()' -> this creates a test client for the Flask app.
#(A test client allows you to simulate HTTP requests and interact with the application
# as if it were running in a web server)

        self.client = app.test_client()

#Here we are using the 'signup' class method on the User class to create a test user in the database.

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
#Here we are committing the changes made to the db session.
#We are ensuring that user and any other data created in the 'setUp' method are saved to the db.
        db.session.commit()

#Here we are testing if a user can successfully add a message in our app.

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

#with self.client as c -> this line starts a context manager for the test client (self.client)
#to simulate a client interacting with the web app

        with self.client as c:

#with c.session_transaction() as sess -> within the client context manager, a session transaction context
#manager is started. This is used to manipulate the session data (simulating a user being logged in) 
#for testing purposes.

            with c.session_transaction() as sess:

#CURR_USER_KEY is a variable used to store the current user's ID.
#Here we are setting the user's ID to self.testuser (which was created during the test setup)
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

#resp=c.post("/messages/new", data={"text":"Hello"}) -> 
# Here we are sending a POST request to the endpoint /messages/new with 
# a data payload that includes a "text" field set to "Hello".
#This is simulating a user posting a message with the text "Hello".

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects

#After making the POST request, we check if the response is equal to 302 which indicates
# a redirect response.            
            self.assertEqual(resp.status_code, 302)
##Addinng additional assert here:
            self.assertEqual(resp.location,'/users/1')

#'msg=Message.query.one()' -> here we are querying the db for a message and assigning it to
#the variable 'msg'. (We are expecting there to only be one message in the db at this point)
            msg = Message.query.one()

#Here we are asserting that the text of the retrieved message is equal to "Hello".
#This confirms that the message with the specified text was successfully added to the db,
#indicating that teh "add message" functionality works as expected.

            self.assertEqual(msg.text, "Hello")

#In summary, this test method simulates a user adding a message to the application by sending
#a POST request, and checks if the message is correctly stored in the db and if the response
#is a redirect.

    # def test_messages_add_get(self):
    #     """Test the GET request for /messages/new"""
    #     with self.app as client:
    #         response = client.get('/messages/new')
    #         self.assertEqual(response.status_code,200)

    def test_messages_add_get(self):
        """Test the GET request for /messages/new."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.get("/messages/new")

      
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"What&#39;s happening?", resp.data)



    def test_show_message_id(self):
        """Does message show when we navigate to /messages/<int:message_id>?"""

        # Simulate a session with the test user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        # Create a test message for the test user within the same session
            message = Message(text='Test message text', user_id=self.testuser.id)
            db.session.add(message)
            db.session.commit()

        # Send a GET request to view the message by its ID
            resp = c.get(f'/messages/{message.id}')

        # Assert that the response status code is 200 (OK)
            self.assertEqual(resp.status_code, 200)

        # Check if the message text is present in the response data
            self.assertIn(b"Test message text", resp.data)

    
    def test_delete_message(self):
        """Test deleting a message."""

          # Simulate a session with the test user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
 # Create a test user
        test_user = User.signup(username="testuser1", email="test@testemail.com", password="testuser1", image_url=None)
        db.session.commit()

        # Create a test message for the test user
        test_message = Message(text="Test message text", user_id=test_user.id)
        db.session.add(test_message)
        db.session.commit()

        # Log in the test user
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = test_user.id

            # Send a POST request to delete the message
            resp = c.post(f'/messages/{test_message.id}/delete')

            # Check if the message is deleted from the database
            deleted_message = Message.query.get(test_message.id)

            # Assert that the response redirects to the user's profile
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, f'/users/{test_user.id}')

            # Assert that the message is deleted (it should return None)
            self.assertIsNone(deleted_message)
 
      

class MessagesViewNoCurrUserTestCase(TestCase):

    def setUp(self):
        self.app = app.test_client()
        db.create_all();

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_messages_add_when_no_user(self):
        #simulate the case where g.user is not set
#when there is no user logged in and they attempt to create a new message,
#  they should be redirected to route('/')
        with app.test_request_context():
            response=self.app.get('/messages/new')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location,'/')

    def test_flash_message_when_no_user(self):
        with app.test_request_context():
            response = self.app.get('/messages/new')
            with self.app.session_transaction() as sess:
                flashed_messages = sess['_flashes']
                self.assertEqual(len(flashed_messages), 1)
                self.assertEqual(flashed_messages[0][0], 'danger')
                self.assertIn('Access unauthorized.', flashed_messages[0][1])


class TestMessageLike(TestCase):
    def setUp(self):
        self.app = app.test_client()
        db.create_all();
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_like(self):
        # Define a test message_id and user_id
        test_message_id = 1
        test_user_id = 1

        # Simulate a logged-in user (you may need to set up user session data)
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = test_user_id  # Set up a mock user session

            # Make a POST request to your route
            response = client.post(f'/messages/{test_message_id}/like')

            # Assert the response status code is as expected
            self.assertEqual(response.status_code, 302) 
            self.assertEqual(response.headers['Location'], '/')


