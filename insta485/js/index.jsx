import React, { useState, useEffect } from "react";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Index() {
  
  const getData = async () => {
    try {
      const response = await fetch('/api/v1/posts/', { credentials: "same-origin" });
      const data = await response.json();
      console.log(data);
    } catch(error) {
      console.error(error);
    }
  }

  useEffect(() => {
    getData();
  }, [])

  return (
    <div>Main Page</div>
  );
}
