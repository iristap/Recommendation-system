import requests
import pandas as pd
import streamlit as st

# API key จาก TMDb
TMDB_API_KEY = '87c828d4cf266c4e630567e9b07e8c08'

# Load the correlation matrix
corrMatrix = pd.read_csv('./corrMatrix.csv', index_col=0)

# Load the movie titles and genres from movies.csv
movies_df = pd.read_csv('./dataset/movies.csv')  # Adjust the path if necessary

# Load the links file (with imdbId and tmdbId)
links_df = pd.read_csv('./dataset/links.csv')  # Ensure link.csv has columns like 'movieId', 'imdbId', 'tmdbId'

def get_genres(movie_title):
    """Get genres for a given movie title."""
    genres = movies_df.loc[movies_df['title'] == movie_title, 'genres']
    return genres.values[0] if not genres.empty else "Genres not available"

def get_tmdb_poster(tmdb_id):
    """Fetch movie poster URL using TMDb API based on tmdbId."""
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'en-US'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return full_poster_url
    return None

def get_similar(movie_name, rating):
    """Calculate similar ratings based on the correlation matrix."""
    similar_ratings = corrMatrix[movie_name] * (rating - 2.5)
    similar_ratings = similar_ratings.sort_values(ascending=False)
    
    # Create a DataFrame from the results
    similar_movies_df = pd.DataFrame(similar_ratings).reset_index()
    similar_movies_df.columns = ['movie', 'similarity_score']  # Rename columns for clarity
    
    return similar_movies_df

def Recommended(user_ratings, recommendations=10):
    """Generate movie recommendations based on user ratings, excluding watched movies."""
    similar_movies_list = []
    watched_movies = {movie for movie, rating in user_ratings}

    for movie, rating in user_ratings:
        similar_movies = get_similar(movie, rating)
        similar_movies_list.append(similar_movies)
    
    similar_movies_df = pd.concat(similar_movies_list, ignore_index=True)
    recommended_movies = similar_movies_df.groupby('movie')['similarity_score'].sum().reset_index()
    recommended_movies = recommended_movies[~recommended_movies['movie'].isin(watched_movies)]
    recommended_movies = recommended_movies.sort_values(by='similarity_score', ascending=False)
    
    return recommended_movies.head(recommendations)

# Set page config
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# Custom CSS
st.markdown(""" 
<style> 
    .stApp { 
        max-width: 1200px; 
        margin: 0 auto; 
    } 
    .movie-card { 
        background-color: #f0f2f6; 
        border-radius: 10px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
    } 
    .movie-title { 
        font-size: 18px; 
        font-weight: bold; 
        margin-bottom: 10px; 
    } 
    .movie-info { 
        font-size: 14px; 
        color: #555; 
    } 
    .rating-stars { 
        color: #ffd700; 
        font-size: 24px; 
    } 
</style> 
""", unsafe_allow_html=True)

# Streamlit app
st.title("🎬 Movie Recommendation System")

# Initialize session state to keep track of user ratings
if 'user_ratings' not in st.session_state:
    st.session_state.user_ratings = []

# Create a two-column layout
col1, col2 = st.columns([1, 2])

# Add movie form in the left column
with col1:
    st.subheader("Rate Movies You've Watched")
    
    with st.form("add_movie_form"):
        selected_movie = st.selectbox("Select a movie", corrMatrix.columns.tolist())
        rating = st.slider("Rate the movie", 1, 5, 3)
        submit_button = st.form_submit_button("Add Movie")
        
        if submit_button:
            st.session_state.user_ratings.append((selected_movie, rating))
            st.success(f"Added: {selected_movie} with rating {rating}")

    # Display added movies
    if st.session_state.user_ratings:
        st.subheader("Your Rated Movies")
        for movie, rating in st.session_state.user_ratings:
            st.markdown(f"""
            <div class="movie-card">
                <div class="movie-title">{movie}</div>
                <div class="movie-info">
                    <span class="rating-stars">{'★' * rating}</span> ({rating}/5)
                </div>
            </div>
            """, unsafe_allow_html=True)

# Recommendations section in the right column
with col2:
    st.subheader("Get Your Movie Recommendations")
    if st.button("Generate Recommendations"):
        if st.session_state.user_ratings:
            recommendations = Recommended(st.session_state.user_ratings)
            st.subheader("Top Recommended Movies")
            
            for index, row in recommendations.iterrows():
                movie_title = row['movie']
                genres = get_genres(movie_title)
                similarity_score = row['similarity_score']

                # Get tmdbId from link.csv
                movie_id = movies_df[movies_df['title'] == movie_title]['movieId'].values[0]
                tmdb_id = links_df[links_df['movieId'] == movie_id]['tmdbId'].values[0]

                # Get poster URL
                poster_url = get_tmdb_poster(tmdb_id)

                # Display movie card with poster
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{poster_url}" alt="{movie_title} poster" width="20%" style="float:left; margin-right: 15px;">
                    <div class="movie-title">{movie_title}</div>
                    <div class="movie-info">
                        <strong>Genres:</strong> {genres.replace('|', ', ')}<br>
                        <strong></strong>
                    </div>
                    <div style="clear:both;"></div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.warning("Please rate at least one movie to get recommendations.")


# Add a footer
st.markdown("---")
st.markdown("Developed by Group 12 ❤️")
