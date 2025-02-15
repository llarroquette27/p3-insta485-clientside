# Project 3 Wrapper

### Q1: What advice would you give future students about debugging React components? {: #Q1}
Use many print statements to see exactly what data you are fetching, how the data is evolving throughout the program, and where it is changing. You can do this via useEffects


Q2a: How did your team design your React components to handle dynamic updates such as likes and comments?
Q2b: How did your team pass data between React components?

### Answer at least one of the two questions above {: #Q2}
a. We use the onClick handler of buttons to identify the event. From there, we sent a POST request to the API to update the database. Then, we fetched new data from the database to make sure we were up to date
b. We only had 2 components, an index component which was like our main function and the post component. For each post component, we passed in the url it needed to fetch from.


### Q3:  How did your team approach the division of work for this project? How did that experience go? {: #Q3}
On the server side, we both did one of the REST api routes together and then evently split up the rest. On the client side, we found it more challenging to split up since it was all one page and very different. We decided to each spend a weekend reading through all the React documentation and then we worked on the client side together.