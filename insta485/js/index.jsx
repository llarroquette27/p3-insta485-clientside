import React, { useState, useEffect, useMemo } from "react";
import Post from "./post";
import InfiniteScroll from 'react-infinite-scroll-component';

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Index() {
  
  const [posts, setPosts] = useState([]);
  const [next, setNext] = useState('/api/v1/posts/');
  const [dataLoaded, setDataLoaded] = useState(false);

  const getData = async (url) => {
    try {
      const response = await fetch(url, { credentials: "same-origin" });
      const responseData = await response.json();
      console.log(responseData)
      setPosts([...posts, ...responseData.results])
      setNext(responseData.next)
      setDataLoaded(true);
    } catch(error) {
      console.error(error);
    }
  }

  useMemo(() => {
    getData(next);
  }, [])

  useEffect(() => {
    console.log(posts)
  }, [posts])

  return (
    <>
      {dataLoaded ? (
      <InfiniteScroll
        dataLength={posts.length}
        next={() => getData(next)}
        hasMore={next !== ''}
        loader={<p>Loading...</p>}
      >
        {posts.map((p, index) => (
          <div key={index}>
            <Post url={p.url} />
          </div>
        ))}
      </InfiniteScroll>
      ) : <div>Loading...</div>}
    </>
  );
}
