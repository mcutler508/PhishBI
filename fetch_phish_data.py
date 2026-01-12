"""
Phish.net API Data Fetcher
Fetches all show data and builds comprehensive Excel dataset for Power BI
"""

import os
import requests
import pandas as pd
import json
from datetime import datetime
import time
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration from environment variables
API_KEY = os.getenv("PHISHNET_API_KEY")
BASE_URL = "https://api.phish.net/v5"

# Validate required environment variables
if not API_KEY:
    print("ERROR: PHISHNET_API_KEY is not set in .env file")
    print("Please create a .env file with your API key (see .env.example)")
    exit(1)

def fetch_api(endpoint, params=None):
    """Fetch data from Phish.net API with error handling"""
    if params is None:
        params = {}
    params['apikey'] = API_KEY
    
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Check for API errors
        if 'error_message' in data and data['error_message']:
            print(f"API Error: {data['error_message']}")
            return None
            
        return data.get('data', data)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None

def fetch_all_shows():
    """Fetch all Phish shows"""
    print("Fetching all shows...")
    
    all_shows = []
    
    # Fetch shows year by year (more reliable than fetching all at once)
    for year in range(1983, 2026):  # 1983-2025
        print(f"  Fetching {year}...")
        shows = fetch_api(f"shows/showyear/{year}.json")
        
        if shows:
            all_shows.extend(shows)
            time.sleep(0.5)  # Rate limiting - be nice to the API
    
    print(f"Total shows fetched: {len(all_shows)}")
    return all_shows

def fetch_all_venues():
    """Fetch all venue data"""
    print("Fetching all venues...")
    venues = fetch_api("venues.json")
    print(f"Total venues fetched: {len(venues) if venues else 0}")
    return venues or []

def fetch_all_songs():
    """Fetch all songs"""
    print("Fetching all songs...")
    songs = fetch_api("songs.json")
    print(f"Total songs fetched: {len(songs) if songs else 0}")
    return songs or []

def fetch_setlist_for_show(showdate):
    """Fetch setlist for a specific show"""
    setlist = fetch_api(f"setlists/showdate/{showdate}.json")
    return setlist

def process_shows_data(shows_data):
    """Process shows data into structured format"""
    print("Processing shows data...")
    
    shows_list = []
    for show in shows_data:
        shows_list.append({
            'ShowID': show.get('showid'),
            'ShowDate': show.get('showdate'),
            'Year': show.get('showyear'),
            'VenueID': show.get('venueid'),
            'VenueName': show.get('venue'),
            'City': show.get('city'),
            'State': show.get('state'),
            'Country': show.get('country'),
            'Artist': show.get('artist', 'Phish'),
            'TourName': show.get('tour_name'),
            'Rating': show.get('rating'),
            'ReviewCount': show.get('reviews_count', 0)
        })
    
    df = pd.DataFrame(shows_list)
    # Convert Year to integer for era calculations
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce').fillna(0).astype(int)
    return df

def process_venues_data(venues_data):
    """Process venue data"""
    print("Processing venues data...")
    
    venues_list = []
    for venue in venues_data:
        venues_list.append({
            'VenueID': venue.get('venueid'),
            'VenueName': venue.get('name'),
            'City': venue.get('city'),
            'State': venue.get('state'),
            'Country': venue.get('country'),
            'PastShowsCount': venue.get('past_shows', 0)
        })
    
    df = pd.DataFrame(venues_list)
    return df

def process_songs_data(songs_data):
    """Process songs data"""
    print("Processing songs data...")
    
    songs_list = []
    for song in songs_data:
        songs_list.append({
            'SongID': song.get('songid'),
            'SongName': song.get('song'),
            'Slug': song.get('slug'),
            'Debut': song.get('debut'),
            'TimesPlayed': song.get('times_played', 0),
            'LastPlayed': song.get('last_played'),
            'Gap': song.get('gap', 0)
        })
    
    df = pd.DataFrame(songs_list)
    return df

def determine_era(year):
    """Determine Phish era from year"""
    if 1983 <= year <= 2000:
        return "1.0"
    elif 2001 <= year <= 2004:
        if year == 2001:
            return "Hiatus 1"
        return "2.0"
    elif 2005 <= year <= 2008:
        return "Hiatus 2"
    elif 2009 <= year <= 2020:
        return "3.0"
    elif year >= 2021:
        return "4.0"
    return "Unknown"

def create_excel_with_formatting(filename, dataframes_dict):
    """Create formatted Excel file with multiple sheets"""
    print(f"Creating Excel file: {filename}")
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get worksheet
            worksheet = writer.sheets[sheet_name]
            
            # Style header row
            header_fill = PatternFill(start_color="00ADB5", end_color="00ADB5", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=11)
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"Excel file created successfully!")

def main():
    """Main execution function"""
    print("=" * 60)
    print("PHISH.NET DATA FETCHER FOR POWER BI")
    print("=" * 60)
    print()
    
    # Fetch all data
    shows_data = fetch_all_shows()
    venues_data = fetch_all_venues()
    songs_data = fetch_all_songs()
    
    if not shows_data:
        print("ERROR: Failed to fetch shows data")
        return
    
    # Process data
    df_shows = process_shows_data(shows_data)
    df_venues = process_venues_data(venues_data) if venues_data else pd.DataFrame()
    df_songs = process_songs_data(songs_data) if songs_data else pd.DataFrame()
    
    # Add Era column to shows
    df_shows['Era'] = df_shows['Year'].apply(determine_era)
    
    # Create summary statistics
    print("Generating summary statistics...")
    
    # Shows by Era
    era_summary = df_shows.groupby('Era').agg({
        'ShowID': 'count',
        'Year': ['min', 'max']
    }).reset_index()
    era_summary.columns = ['Era', 'TotalShows', 'StartYear', 'EndYear']
    era_summary['AvgShowsPerYear'] = era_summary.apply(
        lambda x: x['TotalShows'] / (x['EndYear'] - x['StartYear'] + 1), axis=1
    )
    
    # Shows by State
    state_summary = df_shows.groupby('State').agg({
        'ShowID': 'count',
        'VenueName': 'nunique'
    }).reset_index()
    state_summary.columns = ['State', 'TotalShows', 'UniqueVenues']
    state_summary = state_summary.sort_values('TotalShows', ascending=False)
    
    # Shows by Year
    year_summary = df_shows.groupby('Year').agg({
        'ShowID': 'count'
    }).reset_index()
    year_summary.columns = ['Year', 'ShowCount']
    
    # Top songs (if we have song data)
    if not df_songs.empty:
        top_songs = df_songs.nlargest(50, 'TimesPlayed')[
            ['SongID', 'SongName', 'TimesPlayed', 'Debut', 'LastPlayed', 'Gap']
        ]
    else:
        top_songs = pd.DataFrame()
    
    # Create Excel file
    dataframes = {
        'Fact_Shows': df_shows,
        'Dim_Venues': df_venues,
        'Dim_Songs': df_songs,
        'Fact_Era_Summary': era_summary,
        'Fact_State_Summary': state_summary,
        'Fact_Year_Trend': year_summary,
        'Top_50_Songs': top_songs,
        'Metadata': pd.DataFrame([{
            'DataSource': 'Phish.net API v5',
            'FetchDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'TotalShows': len(df_shows),
            'TotalVenues': len(df_venues),
            'TotalSongs': len(df_songs),
            'YearRange': f"{df_shows['Year'].min()}-{df_shows['Year'].max()}"
        }])
    }
    
    output_file = "Phish_Complete_Data_API.xlsx"
    create_excel_with_formatting(output_file, dataframes)
    
    # Print summary
    print()
    print("=" * 60)
    print("DATA FETCH COMPLETE!")
    print("=" * 60)
    print(f"Total Shows: {len(df_shows):,}")
    print(f"Total Venues: {len(df_venues):,}")
    print(f"Total Songs: {len(df_songs):,}")
    print(f"Year Range: {df_shows['Year'].min()}-{df_shows['Year'].max()}")
    print(f"\nOutput file: {output_file}")
    print()
    print("Shows by Era:")
    print(era_summary.to_string(index=False))
    print()
    print("Top 10 States by Shows:")
    print(state_summary.head(10).to_string(index=False))
    print()
    print("Ready to import into Power BI!")
    print("=" * 60)

if __name__ == "__main__":
    main()
