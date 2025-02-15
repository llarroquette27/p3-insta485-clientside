import React, { useState, useEffect } from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import Post from "./post";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Index() {
  const [posts, setPosts] = useState([]);
  const [next, setNext] = useState("/api/v1/posts/");
  const [dataLoaded, setDataLoaded] = useState(false);

  const getData = async (url) => {
    let ignoreStaleRequest = false;

    try {
      const response = await fetch(url, { credentials: "same-origin" });
      const responseData = await response.json();
      console.log(responseData);

      if (!ignoreStaleRequest) {
        setPosts([...posts, ...responseData.results]);
        setNext(responseData.next);
        setDataLoaded(true);
      }
    } catch (error) {
      console.error(error);
    }

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  };

  // Fetch data for initial render
  useEffect(() => {
    const firstFetch = async () => {
      try {
        const response = await fetch("/api/v1/posts/", {
          credentials: "same-origin",
        });
        const responseData = await response.json();
        console.log(responseData);

        setPosts((prevPosts) => {
          // Create a set of existing post IDs for easy lookup
          const existingPostIds = new Set(prevPosts.map((post) => post.id));

          // Filter out any posts that are already in the state
          const newPosts = responseData.results.filter(
            (post) => !existingPostIds.has(post.id),
          );

          // Append only the new, unique posts
          return [...prevPosts, ...newPosts];
        });
        setNext(responseData.next);
        setDataLoaded(true);
      } catch (error) {
        console.error(error);
      }
    };
    firstFetch();
  }, []);

  return (
    <div>
      {dataLoaded ? (
        <InfiniteScroll
          dataLength={posts.length}
          next={() => getData(next)}
          hasMore={next !== ""}
          loader={<p>Loading...</p>}
        >
          {posts.map((p) => (
            <div key={p.postid}>
              <Post url={p.url} />
            </div>
          ))}
        </InfiniteScroll>
      ) : (
        <div>Loading...</div>
      )}
    </div>
  );
}
