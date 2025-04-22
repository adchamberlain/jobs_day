import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

### Config ###

# List series IDs
series_ids = ["LNS14000000"]  # Unemployment Rate

# List plain-English names for each series.
series_names = {
    "LNS14000000": "U-3 Unemployment Rate (%)"
}

# Define dates 
start_year = datetime.now().year - 10  # Last 10 years of data
end_year = datetime.now().year

# Set API key
api_key = "b3050e233e2649068a3328d1ccbf7aaa"

# Function to get BLS data.
def get_bls_data(series_ids, start_year, end_year):
    """Fetch data from BLS API for specified series and date range"""
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    payload = {
        "seriesid": series_ids,
        "startyear": start_year,
        "endyear": end_year,
        "registrationkey": api_key
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Function to process BLS data and push into Pandas dataframe.
def process_bls_data(raw_data):
    """Convert BLS API response to pandas DataFrame"""
    data_points = []
    
    for series in raw_data["Results"]["series"]:
        series_id = series["seriesID"]
        
        for item in series["data"]:
            year = int(item["year"])
            period = item["period"]
            
            # Convert period (e.g., M01) to month number
            if period.startswith("M"):
                month = int(period[1:])
                date = f"{year}-{month:02d}-01"  # Format as YYYY-MM-DD
                
                data_points.append({
                    "series_id": series_id,
                    "date": date,
                    "value": float(item["value"])
                })
    
    # Create DataFrame and convert date to datetime
    df = pd.DataFrame(data_points)
    df["date"] = pd.to_datetime(df["date"])
    
    # Pivot to wide format with series as columns
    pivot_df = df.pivot(index="date", columns="series_id", values="value")
    
    return pivot_df

def plot_time_series(df, title="BLS Data", subtitle=None, logo_path=None, 
                 line_color='#8B5CF6', grid_color='#E5E7EB', 
                 recession_color='#DBEAFE', text_color='#374151',
                 title_font={'size': 24, 'weight': 'bold'}, 
                 subtitle_font={'size': 18, 'weight': 'normal', 'color': '#6B7280'},
                 add_recession_shading=True, show_current_value=True,
                 x_padding=0.02):  # 2% padding on each side by default
    """
    Create an enhanced time series plot with customizable formatting
    
    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame with datetime index and data columns
    title : str
        Main chart title
    subtitle : str
        Subtitle to display under the main title
    logo_path : str
        Path to company logo image file
    line_color : str
        Color for the data line (hex code or named color)
    grid_color : str
        Color for grid lines
    recession_color : str
        Color for recession shading
    text_color : str
        Color for text elements
    title_font : dict
        Font properties for the title
    subtitle_font : dict
        Font properties for the subtitle
    add_recession_shading : bool
        Whether to add shading for recession periods
    show_current_value : bool
        Whether to show the most recent value as text and horizontal line
    x_padding : float
        Fraction of the x-axis range to add as padding (default: 0.02 or 2%)
    """
    # Set custom style parameters
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.edgecolor'] = grid_color
    plt.rcParams['axes.labelcolor'] = text_color
    plt.rcParams['xtick.color'] = text_color
    plt.rcParams['ytick.color'] = text_color
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Get the data date range
    start_date = df.index.min()
    end_date = df.index.max()
    date_range = end_date - start_date
    padding = pd.Timedelta(days=date_range.days * x_padding)
    
    # Set x-axis limits based on data
    x_min = start_date - padding
    x_max = end_date + padding
    ax.set_xlim(x_min, x_max)
    
    # Add recession shading if requested
    if add_recession_shading:
        # NBER recession dates (start and end dates as YYYY-MM-DD)
        recession_dates = [
            # Historical recessions
            ('2001-03-01', '2001-11-01'),
            ('2007-12-01', '2009-06-01'),
            # COVID-19 recession
            ('2020-02-01', '2020-04-01')
            # Add future recessions as needed
        ]
        
        # Add shaded regions for recessions that overlap with the data
        for start_date_str, end_date_str in recession_dates:
            rec_start = pd.to_datetime(start_date_str)
            rec_end = pd.to_datetime(end_date_str)
            
            # Only draw recessions that overlap with the data's time range
            if not (rec_end < x_min or rec_start > x_max):
                # Clip recession to the data range
                visible_start = max(rec_start, x_min)
                visible_end = min(rec_end, x_max)
                
                ax.axvspan(visible_start, visible_end, 
                          color=recession_color, alpha=0.5, zorder=1)
    
    # Plot data for each column
    for column in df.columns:
        series_name = series_names.get(column, column)
        ax.plot(df.index, df[column], color=line_color, linewidth=2.5, zorder=3, label=series_name)
        
        # Add current value annotation if requested
        if show_current_value:
            current_value = df[column].iloc[-1]
            
            # Add horizontal line at current value
            ax.axhline(current_value, color=line_color, linestyle='--', alpha=0.5, zorder=2)
            
            # Add text for current value - position at end of plot with padding
            text_x_pos = end_date + padding * 0.8  # Position at 80% of the padding
            ax.text(text_x_pos, current_value, f'{current_value:.1f}%', 
                    color=line_color, fontweight='bold', va='center', zorder=4)
    
    # Set title and subtitle
    ax.set_title(title, fontsize=title_font['size'], fontweight=title_font['weight'], 
                color=text_color, pad=20)
    
    if subtitle:
        ax.text(0.5, 0.98, subtitle, transform=ax.transAxes, ha='center',
                fontsize=subtitle_font['size'], fontweight=subtitle_font['weight'],
                color=subtitle_font['color'])
    
    # Format axes
    ax.set_xlabel('', fontsize=12)  # Empty x-label since we have years on x-axis
    ax.set_ylabel('Unemployment Rate (u-%)', fontsize=12)
    
    # Set y-axis limits
    y_max = max(df.max().max() * 1.1, 15)  # Set max to either data max * 1.1 or 15%, whichever is higher
    ax.set_ylim(0, y_max)
    
    # Format x-axis to show years
    from matplotlib.dates import YearLocator, DateFormatter
    ax.xaxis.set_major_locator(YearLocator(4))  # Show every 4 years
    ax.xaxis.set_major_formatter(DateFormatter('%Y'))
    
    # Format grid
    ax.grid(True, color=grid_color, linestyle='-', linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)  # Place grid below data
    
    # Format ticks
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    # Add source citation
    ax.text(0.01, 0.02, 'Source: Bureau of Labor Statistics,\nCurrent Population Survey', 
            transform=ax.transAxes, fontsize=10, color='#6B7280')
    
    # Add logo if path is provided
    if logo_path:
        try:
            logo_img = plt.imread(logo_path)
            logo_ax = fig.add_axes([0.85, 0.02, 0.1, 0.1], anchor='SE', zorder=10)
            logo_ax.imshow(logo_img)
            logo_ax.axis('off')
        except Exception as e:
            print(f"Could not load logo image: {e}")
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, ax
    
# Get data from BLS API
raw_data = get_bls_data(series_ids, start_year, end_year)
    
# Process into DataFrame
df = process_bls_data(raw_data)
    
# Plot the data
# Advanced usage with customization
fig, ax = plot_time_series(
    df, 
    title="Unemployment still low in March",
    subtitle="Unemployment has hovered between 4.0-4.2% since May 2024",
    #logo_path="company_logo.png",  # Add your logo path here
    line_color="#ff7f0e",  # Purple line color
    recession_color="#DBEAFE"  # Light blue recession shading
)
plt.show()
