import React, { useState, useEffect } from "react";
import Post from "./post";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Index() {
  
  const [data, setData] = useState([])

  const getData = async () => {
    try {
      const response = await fetch('/api/v1/posts/', { credentials: "same-origin" });
      const responseData = await response.json();
      console.log(responseData)
      setData(responseData.results)
      
    } catch(error) {
      console.error(error);
    }
  }

  useEffect(() => {
    getData();
  }, [])

  useEffect(() => {
    console.log(data)
  }, [data])

  return (
    <>
       <div>Main Page</div>
       {data.map(p => {
        return (
          <div key={p.postid}>
            <Post url={p.url}/>
          </div>
        )
       })}
    </>
  );
}
