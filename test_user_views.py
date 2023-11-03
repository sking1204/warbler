"""Message View tests.""" 

import os
from unittest import TestCase
from unittest.mock import Mock

from models import db, connect_db, Message, User
from flask import session,g
os.environ['DATABASE_URL'] = "postgresql:///warbler-test" 
from app import app, CURR_USER_KEY 
db.create_all() 
app.config['WTF_CSRF_ENABLED'] = False

class LoginViewTestCase(TestCase):
    """Test login for newly created user."""

  
   
    def setUp(self):
        """Create test client"""

        self.client = app.test_client()  

    def tearDown(self):
        # Clean up the test database
        db.session.remove()
        db.drop_all() 
        db.create_all();  
    

    def test_signup_success(self):
        # Test a successful signup

        with self.client:
            resp= self.client.post('/signup', data={
            'username': 'newtestuser',
            'password': 'welcome21',
            'email': 'newtestuser@example.com',
            'image_url': None
            })

        # Check if the user was redirected to the home page or the URL you expect
        self.assertEqual(resp.status_code, 302)  # 302 is the status code for a redirect
        self.assertEqual(resp.headers['Location'], '/')  # Adjust the URL as needed

class UserViewTestCase(TestCase):
     def setUp(self):
        """Create test client"""

        self.client = app.test_client() 
     

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        db.session.commit()

           
        
        

     def tearDown(self):
        # Clean up the test database
        db.session.remove()
        db.drop_all() 
        db.create_all();  

            

     def test_user_route(self):
         """Testing GET request to /users"""
         with self.client as c:
             with c.session_transaction() as sess:
                 sess[CURR_USER_KEY] = self.testuser.id
                 resp = c.get('/users')
                 self.assertEqual(resp.status_code,200)
                 self.assertIn(b'<p>@testuser</p>', resp.data)

     def test_list_users_with_search(self):
        """Testing using q param in querystring to search by username"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f'/users?q={self.testuser.username}')  
            print(self.testuser.username)
        self.assertEqual(resp.status_code, 200)

     def test_list_users_with_empty_search(self):
        """Testing empty q param in search"""

        ##We expect to see /users?q=
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id         
            resp = c.get('/users?q=')  
        self.assertEqual(resp.status_code, 200)

     def test_user_page_by_id_display(self): 
        """Testing /users/<int:user_id"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id     
            resp = self.client.get(f'/users/{self.testuser.id}')  
            print(self.testuser.id)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"testuser", resp.data)           
        self.assertIn(b"Messages", resp.data)  
        self.assertIn(b"Following", resp.data)  
        self.assertIn(b"Followers", resp.data)  
        self.assertIn(b"Likes", resp.data)  

     def test_non_existing_user_id_page_display(self):
        """Testing page display for user id that doesn't exist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id         
            resp = c.get('/users/999')  
        self.assertEqual(resp.status_code, 404)

     def test_show_following_route(self):
        """Testing the following view """

    #Here we're just checking the view, we're not checking if a user is
    #actually following another user  
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
     
        response = c.get(f'/users/{self.testuser.id}/following')
        self.assertEqual(response.status_code, 200)  

     def test_show_follow_route(self):
        """Testing following user """

    #Here we are tesing selecting of follow button which triggers post request
    #and should redirect
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        
     
        response = c.post(f'/users/follow/{self.testuser2.id}', follow_redirects=True)
        print(self.testuser2.id)
        self.assertEqual(response.status_code, 200)  

     def test_show_followers_route(self):

 #Here we're just checking the view, we're not checking if a user 
 #actually has followers
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
     
        response = c.get(f'/users/{self.testuser.id}/followers')
        self.assertEqual(response.status_code, 200) 

     def test_stop_following_route(self):
     
      #Here we are tesing selecting of unfollow button which triggers post request
    #and should redirect
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        response_follow = c.post(f'/users/follow/{self.testuser2.id}')
        self.assertEqual(response_follow.status_code, 302)

        
     
        response = c.post(f'/users/stop-following/{self.testuser2.id}', follow_redirects=True)
        print(self.testuser2.id)
        self.assertEqual(response.status_code, 200)  

     def test_likes_route(self):

#Here we're just checking the view, we're not checking if a user 
 #actually has likes
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
     
        response = c.get(f'/users/{self.testuser.id}/likes')
        self.assertEqual(response.status_code, 200) 







     def test_add_like(self):
        # Define a test message_id and user_id
        test_message_id = 1
        test_user_id = 1

        # Simulate a logged-in user (you may need to set up user session data)
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user_id'] = test_user_id  # Set up a mock user session

            # Make a POST request to your route
            response = c.post(f'/messages/{test_message_id}/like')

            # Assert the response status code is as expected
            self.assertEqual(response.status_code, 302) 
            self.assertEqual(response.headers['Location'], '/')

     def test_get_profile_authenticated(self):
               
        # Log in the test user  - testing GET request to /profile for logged in user     
            with self.client as c:
                with c.session_transaction() as sess:
                    sess[CURR_USER_KEY] = self.testuser.id
                resp = c.get(f'/users/profile')        
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Edit Your Profile', resp.data)

     def test_edit_profile_valid_data(self):
        # Assuming you have a user object in your database
        # and a user is authenticated for this test
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                print(self.testuser.id)
            response = c.post('/users/profile', data=dict(
                username='testuser',
                email='test@test.com',
                password='testuser',  
                image_url=None,
                header_image_url='/static/images/warbler-hero.jpg',
                bio='new_bio'
            ))     

            self.assertEqual(response.status_code,302)
            self.assertEqual(response.headers['Location'], '/users/1') 


class DeleteUserProfileTestCase(TestCase):
     def setUp(self):
        """Create test client"""

        self.client = app.test_client() 
     
        self.testuser = User.signup(username="testuser8",
                                    email="test8@test.com",
                                    password="testuser8",
                                    image_url=None)
        db.session.commit()


        
        
        
        

     def tearDown(self):
        # Clean up the test database
        db.session.remove()
        db.drop_all() 
        db.create_all();  

     def test_delete_user(self):              

      with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
          

            response = c.post('/users/delete', follow_redirects=True)
            

        
            self.assertEqual(response.status_code, 200)  
            self.assertIn(b' <h2 class="join-message">Join Warbler today.</h2>',response.data)
          

        # Here we are making sure the user has been deleted from the db
            deleted_user = User.query.filter_by(id=self.testuser.id).first()
            self.assertIsNone(deleted_user)

  


    


   




        

        









    # def test_signup_success(self):
    #     # Test a successful signup

       
    #     self.testuser = User.signup(username="testuser",
    #                                 email="test@test.com",
    #                                 password="testuser",
    #                                 image_url=None)
    #     db.session.commit()

    #     with self.client as c:
    #             with c.session_transaction() as sess:
    #                 sess[CURR_USER_KEY] = self.testuser.id
    #             resp = c.post('/signup')

        
                

    #     # Check if the user was redirected to the home page or the URL you expect
    #     self.assertEqual(resp.status_code, 302)  # 302 is the status code for a redirect
    #     self.assertEqual(resp.headers['Location'], '/')  # Adjust the URL as needed
    



    # def test_users_view(self):
    #         with self.client as c:
    #             resp= c.get('/signup')
    #         with self.client as c:
    #             with c.session_transaction() as sess:
    #                 sess[CURR_USER_KEY] = self.testuser.id
    #             resp = c.get('/users')
    #         self.assertEqual(resp.status_code,200)
 
#     def test_login_get(self):

#         with self.client:


#     # Here we are sending a GET request to the login route and validating we get some expected
#     # text back on the page back (this shows us we're actually getting what we expect to see on the login page)

#             resp = self.client.get('/login')        
#         self.assertEqual(resp.status_code, 200)
#         self.assertIn(b"Welcome back.", resp.data)


#Here we want to create a testuser, add to test db, log them in, and validate we are directed where we should be

    # def test_login_valid_credentials_post(self):
        
    #     self.testuser = User.signup(username="testuser",
    #                                 email="test@test.com",
    #                                 password="testuser",
    #                                 image_url=None)

    #     db.session.commit()

    #     with self.client:

    #     # Send a POST request to the login route with valid credentials
    #         resp = self.client.post('/login', data={'username': 'testuser', 'password': 'testuser'})

    #     # Check if the response redirects to the home page (status code 302)
    #         self.assertEqual(resp.status_code, 302)
    #         self.assertEqual(resp.headers['Location'], '/') 

   


# class LogoutRouteTestCase(TestCase):
#     """Testing logout"""
#     def setUp(self):
#         # Set up a test client for the Flask application
#         self.client = app.test_client()


#     def test_logout_user(self) :
#         with self.client:
#             resp = self.client.get('/logout')
#             self.assertEqual(resp.status_code, 302)
#             self.assertEqual(resp.headers['Location'], '/login')



# class UserRouteTestCase(TestCase):
#     """Testing user routes"""

#     def setUp(self):
#         # Set up a test client for the Flask application
#         self.client = app.test_client()

#     def test_users_view(self):
#         with self.client:
#             resp = self.client.get('/users')
#             self.assertEqual(resp.status_code,200)

#     def test_list_users_with_search(self):
#         with self.client:
#             resp = self.client.get('/users?q=testuser')  
#         self.assertEqual(resp.status_code, 200)

#     def test_list_users_with_empty_search(self):
#         with self.client:
#             resp = self.client.get('/users?q=')  
#         self.assertEqual(resp.status_code, 200)

#     def test_user_profile_display(self):
#         response = self.client.get('/users/1')  # Replace 1 with a valid user ID
#         self.assertEqual(response.status_code, 200)  # Check if the response status code is 200 (OK)
#         # self.assertIn(b"User Profile", response.data)  # Check if the page contains "User Profile" in the response content

#     def test_user_not_found(self):
#         resp = self.client.get('/users/999')  # Replace 999 with a non-existing user ID
#         self.assertEqual(resp.status_code, 404)  # Check if the response status code is 404 (Not Found)

# # class TestUserRoute(TestCase):
# #     def setUp(self):
# #         self.app = app.test_client()

# #     def test_user_likes(self):
# #         # Create a mock User object
# #         user_mock = Mock()
# #         user_mock.likes = [Message(id=1), Message(id=2)]  # Replace with sample message objects

# #         # Replace the actual query method with a mock
# #         user_mock.query.get_or_404.return_value = user_mock

# #         with self.mock.patch('your_flask_app.models.User', user_mock):
# #             response = self.app.get('/users/1')  # Replace 1 with a valid user ID
# #             self.assertEqual(response.status_code, 200)

# #             # Check if the likes are rendered in the response content
# #             self.assertIn(b"Likes: [1, 2]", response.data)


        
# class TestUserRoute(TestCase):
#     def setUp(self):
#         self.client = app.test_client()

#         self.testuser2 = User.signup(username="testuser2",
#                                     email="test2@test.com",
#                                     password="testuser2",
#                                     image_url=None)
        
#         db.session.commit()

#     def test_show_user_id(self):
#     #     """Test user_id route."""
#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.testuser2.id
#                 resp = c.get(f'/users/{self.testuser2.id}')

#         self.assertEqual(resp.status_code, 200)

#         # Check if the user's username is present in the response data
#         self.assertIn(b"testuser2", resp.data)  

# class TestUserFollowingRoute(TestCase):
   
#     def setUp(self):
#         # Create a test user
    
#         self.client = app.test_client()

#         self.testuser = User.signup(username="testuser3",
#                                     email="test3@test.com",
#                                     password="testuser3",
#                                     image_url=None)
#         db.session.commit()

# #Here we're just checking the view, we're not checking if a user is
# #actually following another user

#     def test_show_following_route(self):
#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.testuser.id
     
#         response = c.get('/users/1/following')
#         self.assertEqual(response.status_code, 200)  

# class TestUserFollowersRoute(TestCase):
   
#     def setUp(self):
#         # Create a test user
    
#         self.client = app.test_client()

#         self.testuser = User.signup(username="testuser4",
#                                     email="test4@test.com",
#                                     password="testuser4",
#                                     image_url=None)
#         db.session.commit()

#     def test_show_follow_route(self):
#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.testuser.id
     
#         response = c.post('/users/follow/1', follow_redirects=True)
#         self.assertEqual(response.status_code, 200)  

# class TestStopFollowingRoutes(TestCase):

#      def setUp(self):
#         # Create a test user
    
#         self.client = app.test_client()

#         self.testuser = User.signup(username="testuser5",
#                                     email="test5@test.com",
#                                     password="testuser5",
#                                     image_url=None)
#         db.session.commit()





#      def test_stop_following(self):
#         # Assuming you have a test user already created
#         with self.client as c:
#             with app.app_context():
#                 g.user = self.testuser
        
        

#         # Make a POST request to the stop_following route
#         follow_id = 1  # ID to unfollow
#         response = c.post(f'/users/stop-following/{follow_id}')

#         # Assert that the response is a redirect to the following page
#         self.assertEqual(response.status_code, 302)
#         # self.assertEqual(response.location, f'http:///users/{self.testuser.id}/following')

# class TestShowLikeRoutes(TestCase):
#     class TestStopFollowingRoutes(TestCase):

#      def setUp(self):
#         # Create a test user
    
#         with app.test_request_context('/users/1/likes'):
#             with app.test_client() as client:
#                 with client.session_transaction() as sess:
#                     sess['user_id'] = 1

#             response = client.get('/users/1/likes')
#             self.assertEqual(response.status_code, 200)


# #as far as testing content resposne on likes page...there's nothing really distinct that we could test for
# #especailly since we can still navigate to the likes page if the user hasn't liked anything, so we couldn't 
# #call out/ assert something like <i class="fa fa-thumbs-up"></i>  in resp.data.
                 
# class EditProfileRouteTestCase(TestCase):

#     def setUp(self):
#         # Create a test user
    
#         self.client = app.test_client()

#         self.testuser = User.signup(username="testuser7",
#                                     email="test7@test.com",
#                                     password="testuser7",
#                                     image_url=None)
#         db.session.commit()


#     def test_get_profile_authenticated(self):
               
#         # Log in the test user  - testing GET request to /profile for logged in user     
#             with self.client as c:
#                 with c.session_transaction() as sess:
#                     sess[CURR_USER_KEY] = self.testuser.id
#                 resp = c.get(f'/users/profile')        
#             self.assertEqual(resp.status_code, 200)
#             self.assertIn(b'Edit Your Profile', resp.data)

# class EditProfilePOSTRouteTestCase (TestCase):
#     def setUp(self):
#         self.client = app.test_client()
#         self.testuser = User.signup(username="testuser8",
#                                     email="test8@test.com",
#                                     password="testuser8",
#                                     image_url=None)
#         db.session.commit()

       

#     def test_edit_profile_valid_data(self):
#         # Assuming you have a user object in your database
#         # and a user is authenticated for this test
#         with self.client as c:
#             with c.session_transaction() as sess:
#                 sess[CURR_USER_KEY] = self.testuser.id
#                 print(self.testuser.id)
#             response = c.post('/users/profile', data=dict(
#                 username='testuser8',
#                 email='test8@test.com',
#                 password='testuser8',  # Provide a valid password
#                 image_url=None,
#                 header_image_url='/static/images/warbler-hero.jpg',
#                 bio='new_bio'
#             ))     

#             self.assertEqual(response.status_code,302)
# ## Might have bug/error here. Looks like new record is being created instead of edited.
# ## we are being redirected to /users/2
# ##commenting out for now...needs further research
#             # self.assertEqual(response.headers['Location'], '/users/1') 

# ##When I try to add the delete route...tests begin to break/

# # class DeleteUserRouteTestCase(TestCase):
# #     def setUp(self):
# #         self.client = app.test_client()

# #         self.testuser= User.signup(username="testuser9",
# #                               email="test9@test.com",
# #                               password="testuser9",
# #                               image_url=None)
# #         db.session.commit()

# #     def test_delete_user(self):
# #         with app.test_request_context('/'):  # Create a request context
# #             with self.client as c:
# #                 g.user = self.testuser  # Set the user in the context

# #             with c.session_transaction() as session:
# #                 session[CURR_USER_KEY] = g.user.id

# #             resp = self.client.post('/users/delete')
# #             self.assertEqual(resp.status_code, 302)  # Check for redirect status code
# #             # Check if the user is redirected to '/'
# #             self.assertEqual(resp.location, '/')

# #             # Check if the user is no longer in the database
# #             deleted_user = User.query.get(g.user.id)
# #             self.assertIsNone(deleted_user)

# #             # Check if the session is cleared after deleting the user
# #             with c.session_transaction() as session:
# #                 self.assertNotIn(CURR_USER_KEY, session)

# #     def tearDown(self):
# #         # Roll back the database transaction to keep it isolated
# #         db.session.rollback()






            
         

    




    

    

      
    
    



    
        

        





       





        
          
    

       
        

