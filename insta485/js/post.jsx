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
          setTime(data.created);
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
  

  const handleDoubleClick = async () => {
    if (isLiked === false) {
      handleLike();
    }
  };

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
  // ADD: Comment owner link, like button, comment button, humanized timestamp
  return (
    <div className="post">
      <p>{owner}</p>
      <img src={profilePic} alt="profile_pic"/>
      <p>{time}</p>
      <img src={imgUrl} alt="post_image" onDoubleClick={handleDoubleClick}/>
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
        // <form action="/likes/" method="post" enctype="multipart/form-data">
        //   <input type="hidden" name="operation" value="unlike" />
        //   <input type="hidden" name="postid" value="{{ post.postid }}" />
        //   <input type="submit" name="unlike" value="unlike" />
        // </form>
      ) : (
        <button 
          data-testid="like-unlike-button"
          onClick={() => handleLike()}
        >
          like
        </button>
        // <form action="/likes/" method="post" enctype="multipart/form-data">
        //   <input type="hidden" name="operation" value="like" />
        //   <input type="hidden" name="postid" value="{{ post.postid }}" />
        //   <input type="submit" name="like" value="like" />
        // </form>
      )}
      {comments.map((c, index) => {
        return (
          <div>
            <a href={c.ownerShowUrl}>{c.owner}</a>
            <span>{c.text}</span>
          </div>
        )
      })}
      <button></button>
      {/* <form action="/comments/" method="post" enctype="multipart/form-data">
        <input type="hidden" name="operation" value="create" />
        <input type="hidden" name="postid" value="{{post.postid}}" />
        <input type="text" name="text" required />
        <input type="submit" name="comment" value="comment" />
      </form> */}
    </div>
  );
}
