import pandas as pd
import streamlit as st

# Load the correlation matrix
corrMatrix = pd.read_csv('./corrMatrix.csv', index_col=0)

def get_similar(movie_name, rating):
    """Calculate similar ratings based on the correlation matrix."""
    similar_ratings = corrMatrix[movie_name] * (rating - 2.5)
    similar_ratings = similar_ratings.sort_values(ascending=False)
    
    # Create a DataFrame from the results
    similar_movies_df = pd.DataFrame(similar_ratings).reset_index()
    similar_movies_df.columns = ['movie', 'similarity_score']  # Rename columns for clarity
    
    return similar_movies_df

def Recommended(user_ratings):
    """
    Generate movie recommendations based on user ratings,
    excluding movies that the user has already watched.
    """
    
    # List to collect similar movie DataFrames
    similar_movies_list = []
    
    # Set of watched movies for filtering
    watched_movies = {movie for movie, rating in user_ratings}
    
    # Iterate through each rated movie and its corresponding rating
    for movie, rating in user_ratings:
        similar_movies = get_similar(movie, rating)
        similar_movies_list.append(similar_movies)
    
    # Concatenate all similar movies DataFrames
    similar_movies_df = pd.concat(similar_movies_list, ignore_index=True)
    
    # Aggregate similarity scores by movie name
    recommended_movies = similar_movies_df.groupby('movie')['similarity_score'].sum().reset_index()
    
    # Filter out movies that the user has already watched
    recommended_movies = recommended_movies[~recommended_movies['movie'].isin(watched_movies)]
    
    # Sort the recommended movies by aggregated similarity score in descending order
    recommended_movies = recommended_movies.sort_values(by='similarity_score', ascending=False)
    
    return recommended_movies

# Streamlit app
st.title("Movie Recommendation System")

# Initialize session state to keep track of user ratings
if 'user_ratings' not in st.session_state:
    st.session_state.user_ratings = []

# Dropdown for movie selection
movie_list = corrMatrix.columns.tolist()  # Get the list of movies from the correlation matrix

# Create a form to add movies and ratings
with st.form("movie_form"):
    st.subheader("Add Movies You've Watched")
    
    # Dropdown for movie selection
    selected_movie = st.selectbox("Select a movie", movie_list)
    
    # Slider for rating
    rating = st.slider("Rate the movie", 1, 5, 3)  # Rating from 1 to 5, default is 3
    
    # Add movie button
    if st.form_submit_button("Add Movie"):
        st.session_state.user_ratings.append((selected_movie, rating))
        st.success(f"Added: {selected_movie} with rating {rating}")

# Display added movies
if st.session_state.user_ratings:
    st.subheader("Movies You've Watched")
    for movie, rating in st.session_state.user_ratings:
        st.write(f"{movie} - Rating: {rating}")

# Button to get recommendations
if st.button("Get Recommendations"):
    if st.session_state.user_ratings:
        recommendations = Recommended(st.session_state.user_ratings)
        st.subheader("Recommended Movies")
        st.write(recommendations.head(10))  # Display top 10 recommended movies
    else:
        st.warning("Please add at least one movie to get recommendations.")
