import React, { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import Index from "./index";

// Create a root
const root = createRoot(document.getElementById("reactEntry"));

// Insert the post component into the DOM.  Only call root.render() once.
root.render(
  <StrictMode>
    {/* <Post url="/api/v1/posts/1/" /> */}
    <Index />
  </StrictMode>,
);
