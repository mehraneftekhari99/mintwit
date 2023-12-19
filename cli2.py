import cmd
import requests


class SocialNetworkCLI(cmd.Cmd):
    prompt = "(social-network) "
    api_url = "http://localhost:5000"  # Change if your API is hosted elsewhere
    current_user = None

    def do_exit(self, arg):
        """Exit the application."""
        return True

    def do_create_user(self, username):
        """Create a new user. Usage: create_user [username]"""
        if not username:
            print("Username is required.")
            return
        response = requests.post(f"{self.api_url}/register", json={"username": username})
        if response.status_code == 201:
            self.current_user = response.json()["user_id"]
            print(f"User '{username}' created and logged in as user ID {self.current_user}.")
        else:
            print(f"Error: {response.json().get('error')}")

    def do_list_users(self, arg):
        """List all users. Usage: list_users"""
        response = requests.get(f"{self.api_url}/users")
        if response.status_code == 200:
            for user in response.json()["users"]:
                print(f"User ID {user['id']}: {user['username']}")
        else:
            print("Error fetching users.")

    def do_switch_user(self, user_id):
        """Switch to another user. Usage: switch_user [user_id]"""
        try:
            user_id = int(user_id)
        except ValueError:
            print("Invalid user ID.")
            return
        response = requests.get(f"{self.api_url}/users")
        if user_id in [user["id"] for user in response.json()["users"]]:
            self.current_user = user_id
            print(f"Switched to user ID {self.current_user}.")
        else:
            print("User not found.")

    def do_tweet(self, content):
        """Post a new tweet. Usage: tweet [content]"""
        if not self.current_user:
            print("Please switch to a user first.")
            return
        if not content:
            print("Content is required.")
            return
        response = requests.post(
            f"{self.api_url}/tweet", json={"user_id": self.current_user, "content": content}
        )
        if response.status_code == 201:
            print("Tweet posted.")
        else:
            print(f"Error: {response.json().get('error')}")

    def do_follow(self, followee_id):
        """Follow a user. Usage: follow [user_id]"""
        if not self.current_user:
            print("Please switch to a user first.")
            return
        try:
            followee_id = int(followee_id)
        except ValueError:
            print("Invalid user ID.")
            return
        response = requests.post(
            f"{self.api_url}/follow",
            json={"follower_id": self.current_user, "followee_id": followee_id},
        )
        if response.status_code == 200:
            print(f"Followed user ID {followee_id}.")
        else:
            print(f"Error: {response.json().get('error')}")

    def do_unfollow(self, followee_id):
        """Unfollow a user. Usage: unfollow [user_id]"""
        if not self.current_user:
            print("Please switch to a user first.")
            return
        try:
            followee_id = int(followee_id)
        except ValueError:
            print("Invalid user ID.")
            return
        response = requests.post(
            f"{self.api_url}/unfollow",
            json={"follower_id": self.current_user, "followee_id": followee_id},
        )
        if response.status_code == 200:
            print(f"Unfollowed user ID {followee_id}.")
        else:
            print(f"Error: {response.json().get('error')}")

    def do_followers(self, arg):
        """List followers of the current user. Usage: followers"""
        if not self.current_user:
            print("Please switch to a user first.")
            return
        response = requests.get(f"{self.api_url}/followers", params={"user_id": self.current_user})
        if response.status_code == 200:
            for user in response.json()["followers"]:
                print(f"User ID {user['id']}: {user['username']}")
        else:
            print("Error fetching followers.")

    def do_following(self, arg):
        """List users the current user is following. Usage: following"""
        if not self.current_user:
            print("Please switch to a user first.")
            return
        response = requests.get(f"{self.api_url}/following", params={"user_id": self.current_user})
        if response.status_code == 200:
            for user in response.json()["following"]:
                print(f"User ID {user['id']}: {user['username']}")
        else:
            print("Error fetching following.")

    def do_feed(self, arg):
        """View the user's feed. Usage: feed [page] [per_page]"""
        if not self.current_user:
            print("Please switch to a user first.")
            return
        args = arg.split()
        page = int(args[0]) if args and args[0].isdigit() else 1
        per_page = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
        response = requests.get(
            f"{self.api_url}/feed",
            params={"user_id": self.current_user, "page": page, "per_page": per_page},
        )
        if response.status_code == 200:
            for tweet in response.json()["tweets"]:
                print(f"{tweet['id']}: {tweet['content']} (by user {tweet['user_id']})")
        else:
            print("Error fetching feed.")

    def do_explore(self, arg):
        """View the latest tweets from all users. Usage: explore [page] [per_page]"""
        args = arg.split()
        page = int(args[0]) if args and args[0].isdigit() else 1
        per_page = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
        response = requests.get(
            f"{self.api_url}/explore", params={"page": page, "per_page": per_page}
        )
        if response.status_code == 200:
            tweets = response.json()["tweets"]
            if not tweets:
                print("No tweets found.")
            else:
                for tweet in tweets:
                    print(f"{tweet['id']}: {tweet['content']} (by user {tweet['user_id']})")
        else:
            print("Error fetching explore.")


if __name__ == "__main__":
    SocialNetworkCLI().cmdloop()
