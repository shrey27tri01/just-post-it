from django.test import TestCase, Client
from .models import User, Profile, Tweet, FollowerRelation
import json

# Create your tests here.
class TweetsTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="usinguser1", email="user1@user.com")
        self.user2 = User.objects.create_user(username="user2", password="usinguser2", email="user2@user.com")
        self.tweet1 = Tweet.objects.create(content="tweet1", user=self.user1)
        self.tweet2 = Tweet.objects.create(content="tweet2", user=self.user1)
        self.tweet3 = Tweet.objects.create(content="tweet3", user=self.user2)

    def testTweetCreated(self):
        tweetObj = Tweet.objects.create(content="tweet4", user=self.user1)
        self.assertEqual(tweetObj.id, 4)
        self.assertEqual(tweetObj.user, self.user1)

    def testTweetCount(self):
        count = Tweet.objects.count()
        self.assertEqual(count, 3)
    
    def testUserCount(self):
        count = User.objects.count()
        self.assertEqual(count, 2)
    
    def testTweet1Like(self):
        self.tweet1.likes.add(self.user2)
        count = self.tweet1.likes.all().count()
        self.assertEqual(count, 1)
    
    def testUser1Follow(self):
        self.user1.profile.followers.add(self.user2)
        countFollowers = self.user1.profile.followers.count()
        countFollowing = self.user2.following.count()
        self.assertEqual(countFollowers, 1)
        self.assertEqual(countFollowing, 1)
        
    def getClient(self):
        client = Client()
        client.login(username=self.user2.username, password="usinguser2")
        return client
    
    def testAllTweetList(self):
        client = self.getClient()
        response = client.get("/all/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["allTweets"].count(), 3)
        self.assertEqual(response.context["currentuser"], self.user2)
    
    def testTweetRelatedName(self):
        user2 = self.user2
        user1 = self.user1
        self.assertEqual(user2.tweets.count(), 1)
        self.assertEqual(user1.tweets.count(), 2)
    
    def testTweetCreatethroughClient(self):
        client = self.getClient()
        response = client.post("/create/", data={"tweet_content": "tweet4"})
        newTweet = Tweet.objects.get(id=4)
        self.assertEqual(Tweet.objects.count(), 4)
        self.assertEqual(newTweet.user, self.user2)
        self.assertEqual(newTweet.content, "tweet4")
    
    def testIndexView(self):
        client = self.getClient()
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["allTweets"].count(), 1)
    
    def testIndexViewAfterCreate(self):
        client = self.getClient()
        response = client.post("/create/", data={"tweet_content": "tweet4"})
        newTweet = Tweet.objects.get(id=4)
        self.assertEqual(Tweet.objects.count(), 4)
        self.assertEqual(newTweet.user, self.user2)
        self.assertEqual(newTweet.content, "tweet4")
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["allTweets"].count(), 2)

    def testFollowing(self):
        self.user1.profile.followers.add(self.user2)
        client = self.getClient()
        response = client.get("/following/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["currentuser"], self.user2)
        self.assertEqual(len(response.context["tweets"]), 2)
    
    def testEditTweet(self):
        client = self.getClient()
        tweetId = self.tweet3.id
        response = client.post(f"/edit/{tweetId}", {"content": "newTweet3"}, HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        responseData = response.json()
        self.assertEqual(responseData.get("response"), "success")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tweet.objects.get(id=3).content, "newTweet3")
    
    def testInvalidMethodEdit(self):
        client = self.getClient()
        tweetId = self.tweet3.id
        response = client.get(f"/edit/{tweetId}", {"content": "newTweet3"}, HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        self.assertEqual(response.status_code, 405)
    
    def testOwnTweetLike(self):
        client = self.getClient()
        tweetId = self.tweet3.id
        response = client.post(f"/like/{tweetId}")
        self.assertEqual(response.status_code, 403)

    def testOtherTweetLike(self):
        client = self.getClient()
        tweetId = self.tweet1.id
        response = client.post(f"/like/{tweetId}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tweet1.likes.count(), 1)    
        responseData = response.json()
        self.assertEqual(responseData.get("action"), "liked")   
        self.assertEqual(responseData.get("likeCount"), 1) 
    
    def testOtherTweetUnlike(self):
        client = self.getClient()
        tweetId = self.tweet1.id
        response = client.post(f"/like/{tweetId}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tweet1.likes.count(), 1)    
        responseData = response.json()
        self.assertEqual(responseData.get("action"), "liked")   
        self.assertEqual(responseData.get("likeCount"), 1)
        response = client.post(f"/like/{tweetId}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tweet1.likes.count(), 0)
        responseData = response.json()
        self.assertEqual(responseData.get("action"), "unliked")   
        self.assertEqual(responseData.get("likeCount"), 0)
    
    def testInvalidMethodLike(self):
        client = self.getClient()
        tweetId = self.tweet2.id
        response = client.get(f"/like/{tweetId}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        self.assertEqual(response.status_code, 405)
    
    def testProfileCreatedViaSignal(self):
        profilesCount = Profile.objects.count()
        self.assertEqual(profilesCount, 2)
    
    def testFollowingThroughModelQueries(self):
        user1 = self.user1
        user2 = self.user2
        user1.profile.followers.add(user2)
        user2Following = user2.following.all()
        querySet = user2Following.filter(user=user1)
        user1FollowingNoOne = user1.following.all()
        self.assertTrue(querySet.exists())
        self.assertFalse(user1FollowingNoOne.exists()) 

    def testFollowingThroughClient(self):
        client = self.getClient()
        user1 = self.user1
        response = client.post(f"/user/{user1.username}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user1.profile.followers.count(), 1)
        self.assertTrue(user1.profile.followers.all().filter(username=self.user2.username).exists())
        responseData = response.json()
        self.assertEqual(responseData.get("response"), "success")
        self.assertEqual(responseData.get("followerCount"), 1)
        self.assertEqual(responseData.get("action"), "followed")
    
    def testFollowYourself(self):
        client = self.getClient()
        user2 = self.user2
        response = client.post(f"/user/{user2.username}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        self.assertEqual(response.status_code, 403)
    
    def testUnfollow(self):
        client = self.getClient()
        user1 = self.user1
        response = client.post(f"/user/{user1.username}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        response = client.post(f"/user/{user1.username}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        self.assertEqual(user1.profile.followers.count(), 0)
        self.assertEqual(response.status_code, 200)
        responseData = response.json()
        self.assertEqual(responseData.get("followerCount"), 0)
        self.assertEqual(responseData.get("response"), "success")
        self.assertEqual(responseData.get("action"), "unfollowed")
    
    def testSelfUserProfile(self):
        client = self.getClient()
        response = client.get(f"/user/{self.user2.username}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["followingCount"], 0)
        self.assertEqual(response.context["followerCount"], 0)
        self.assertEqual(response.context["usertweets"].count(), 1)
        self.assertEqual(response.context["username"], "user2")
    
    def testOtherUserProfile(self):
        client = self.getClient()
        response = client.get(f"/user/{self.user1.username}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["followingCount"], 0)
        self.assertEqual(response.context["followerCount"], 0)
        self.assertEqual(response.context["usertweets"].count(), 2)
        self.assertEqual(response.context["username"], "user1")

    def testOtherUserProfileAfterFollowing(self):
        client = self.getClient()
        response = client.post(f"/user/{self.user1.username}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        response = client.get(f"/user/{self.user1.username}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["followingCount"], 0)
        self.assertEqual(response.context["followerCount"], 1)
        self.assertEqual(response.context["usertweets"].count(), 2)
        self.assertEqual(response.context["username"], "user1")
        
    def testOwnProfileAfterFollowing(self):
        client = self.getClient()
        response = client.post(f"/user/{self.user1.username}", HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/json')
        response = client.get(f"/user/{self.user2.username}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["followingCount"], 1)
        self.assertEqual(response.context["followerCount"], 0)
        self.assertEqual(response.context["usertweets"].count(), 1)
        self.assertEqual(response.context["username"], "user2")
    
    def testRegisterNewUserThroughClient(self):
        client = self.getClient()
        data = {
            "username": "user3",
            "email": "user3@user.com",
            "password": "usinguser3",
            "confirmation": "usinguser3"
        }
        response = client.post("/register/", data)
        self.assertEqual(User.objects.count(), 3)
        self.assertTrue(User.objects.filter(username="user3").exists())


