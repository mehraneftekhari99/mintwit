from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
from waitress import serve

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///social_network.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    in_reply_to_tweet_id = db.Column(db.Integer, db.ForeignKey("tweet.id"), nullable=True)


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    followee_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))


@app.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "user_id": user.id}), 201


@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify({"users": [{"id": user.id, "username": user.username} for user in users]}), 200


@app.route("/follow", methods=["POST"])
def follow():
    follower_id = request.json.get("follower_id")
    followee_id = request.json.get("followee_id")
    if follower_id == followee_id:
        return jsonify({"error": "Cannot follow yourself"}), 400
    follow = Follow(follower_id=follower_id, followee_id=followee_id)
    db.session.add(follow)
    db.session.commit()
    return jsonify({"message": "Followed successfully"}), 200


@app.route("/unfollow", methods=["POST"])
def unfollow():
    follower_id = request.json.get("follower_id")
    followee_id = request.json.get("followee_id")
    Follow.query.filter_by(follower_id=follower_id, followee_id=followee_id).delete()
    db.session.commit()
    return jsonify({"message": "Unfollowed successfully"}), 200


@app.route("/followers", methods=["GET"])
def get_followers():
    user_id = request.args.get("user_id")
    followers = Follow.query.filter_by(followee_id=user_id).all()
    follower_ids = [follower.follower_id for follower in followers]
    follower_users = User.query.filter(User.id.in_(follower_ids)).all()
    return jsonify({"followers": [{"id": user.id, "username": user.username} for user in follower_users]}), 200


@app.route("/following", methods=["GET"])
def get_following():
    user_id = request.args.get("user_id")
    following = Follow.query.filter_by(follower_id=user_id).all()
    following_ids = [followee.followee_id for followee in following]
    following_users = User.query.filter(User.id.in_(following_ids)).all()
    return jsonify({"following": [{"id": user.id, "username": user.username} for user in following_users]}), 200


@app.route("/tweet", methods=["POST"])
def tweet():
    user_id = request.json.get("user_id")
    content = request.json.get("content")
    in_reply_to_tweet_id = request.json.get("in_reply_to_tweet_id")
    tweet = Tweet(user_id=user_id, content=content, in_reply_to_tweet_id=in_reply_to_tweet_id)
    db.session.add(tweet)
    db.session.commit()
    return jsonify({"message": "Tweet created successfully", "tweet_id": tweet.id}), 201


@app.route("/feed", methods=["GET"])
def get_feed():
    user_id = request.args.get("user_id")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    followed_users = [f.followee_id for f in Follow.query.filter_by(follower_id=user_id)]
    feed_query = Tweet.query.filter(Tweet.user_id.in_(followed_users)).order_by(Tweet.created_at.desc())

    paginated_tweets = feed_query.paginate(page=page, per_page=per_page, error_out=False)
    tweets = paginated_tweets.items
    return (
        jsonify({"tweets": [{"id": tweet.id, "content": tweet.content, "user_id": tweet.user_id} for tweet in tweets]}),
        200,
    )


# Get a sample of latest tweets from all users
@app.route("/explore", methods=["GET"])
def get_explore():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    tweets = Tweet.query.order_by(Tweet.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False).items
    return (
        jsonify({"tweets": [{"id": tweet.id, "content": tweet.content, "user_id": tweet.user_id} for tweet in tweets]}),
        200,
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    serve(app, listen="*:5000")
