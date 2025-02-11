import React, { useState, useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [postInfo, setPostInfo] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [owner, setOwner] = useState("");
  const [profilePic, setProfilePic] = useState("");
  const [time, setTime] = useState("");
  const [likes, setLikes] = useState(0);
  const [comments, setComments] = useState([]);
  const [isLiked, setIsLiked] = useState(false);
  const [commentText, setCommentText] = useState('');

  const newLogname = document.getElementById("logname").innerHTML;

  const getInitialData = () => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        console.log("DATA: ", data);
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          setPostInfo(data);
          setImgUrl(data.imgUrl);
          setOwner(data.owner);
          setProfilePic(data.ownerImgUrl);
          setTime(dayjs.utc(data.created).fromNow());
          setLikes(data.likes.numLikes);
          setComments(data.comments);
          setIsLiked(data.likes.lognameLikesThis);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }

  useEffect(() => {
    getInitialData();
  }, [url]);

  const handleComment = async () => {
    try {
      const response = await fetch(`${postInfo.comments_url}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"text": commentText})
      })
      console.log("Success: ", response);
    }
    catch (error) {
      console.error("Error: ", error);
    }

    getInitialData();
    setCommentText('');
  }

  const handleChange = (e) => {
    setCommentText(e.target.value);
  }

  const deleteComment = async (url) => {
    try {
      const response = await fetch(url, {method: "DELETE"});
      console.log("SUCCESS: ", response);
    } catch (error) {
      console.error('Error: ', error);
    }
    getInitialData();
  }

  const handleLike = async () => {
    setIsLiked(true);
    setLikes(likes + 1);

    // Post to rest API
    try {
      console.log("URL: ", `/api/v1/likes/?postid=${postInfo.postid}`)
      const response = await fetch(`/api/v1/likes/?postid=${postInfo.postid}`, {method: "POST"});
      const data = await response.json();
      console.log("SUCCESS: ", data);
    } catch (error) {
      console.error('Error: ', error);
    }
    getInitialData();
  };

  const handleDislike = async () => {
    setIsLiked(false);
    setLikes(likes - 1);

    // Post to rest API
    try {
      console.log("URL: ", `${postInfo.likes.url}`)
      const response = await fetch(`${postInfo.likes.url}`, {method: "DELETE"});
      console.log("SUCCESS: ", response);
    } catch (error) {
      console.error('Error: ', error);
    }
    getInitialData();
  };

  // Render post image and post owner
  return (
    <div className="post">
      <p>{owner}</p>
      <img src={profilePic} alt="profile_pic" />
      <p>{time}</p>
      <img src={imgUrl} alt="post_image" />
      {likes === 1 ? (
        <div>{likes} like</div>
      ) : (
        <div>{likes} likes</div>
      )}
      {isLiked ? (
        <button 
          data-testid="like-unlike-button"
          onClick={() => handleDislike()}
        >
          unlike
        </button>
      ) : (
        <button 
          data-testid="like-unlike-button"
          onClick={() => handleLike()}
        >
          like
        </button>
      )}
      {comments.map((c, index) => {
        return (
          <div>
            <a href={c.ownerShowUrl}>{c.owner}</a>
            <span>{c.text}</span>
            {c.owner === newLogname && (
              <button
                onClick={() => deleteComment(c.url)}
              >Delete comment</button>
            )}
          </div>
        )
      })}
      <form 
        onSubmit={e => {
          e.preventDefault();
          handleComment();
        }} 
        onChange={handleChange}
        enctype="multipart/form-data">
        <input type="text" name="text" required value={commentText}/>
      </form>
    </div>
  );
}
