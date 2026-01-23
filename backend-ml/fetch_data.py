from supabase import create_client, Client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY

def fetch_financial_data():
    """
    Fetch financial data from Supabase
    Returns: pandas DataFrame with financial data
    """
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Fetch financial data
        response = supabase.table('financials').select('*').execute()
        
        # Convert to DataFrame
        df = pd.DataFrame(response.data)
        
        if df.empty:
            print("No data found in financials table")
            return None
        
        # Convert tanggal to datetime
        df['tanggal'] = pd.to_datetime(df['tanggal'])
        
        # Sort by date
        df = df.sort_values('tanggal')
        
        print(f"Fetched {len(df)} records from Supabase")
        print(f"Date range: {df['tanggal'].min()} to {df['tanggal'].max()}")
        print(f"\nData columns: {df.columns.tolist()}")
        print(f"\nData types:")
        print(df['tipe'].value_counts())
        
        return df
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_revenue_data():
    """
    Get only Pemasukan (revenue) data
    Returns: pandas DataFrame with revenue data aggregated by date
    """
    df = fetch_financial_data()
    
    if df is None:
        return None
    
    # Filter only Pemasukan (revenue)
    revenue_df = df[df['tipe'] == 'Pemasukan'].copy()
    
    # Group by date and sum the revenue
    daily_revenue = revenue_df.groupby('tanggal')['jumlah'].sum().reset_index()
    daily_revenue.columns = ['date', 'revenue']
    
    print(f"\nRevenue data prepared: {len(daily_revenue)} days")
    print(f"Total revenue: Rp {daily_revenue['revenue'].sum():,.0f}")
    print(f"Average daily revenue: Rp {daily_revenue['revenue'].mean():,.0f}")
    
    return daily_revenue

if __name__ == "__main__":
    # Test the functions
    print("Testing data fetch from Supabase...\n")
    
    # Fetch all financial data
    df = fetch_financial_data()
    
    if df is not None:
        print("\n" + "="*50)
        print("Sample data:")
        print(df.head())
        
        print("\n" + "="*50)
        # Get revenue data
        revenue_df = get_revenue_data()
        
        if revenue_df is not None:
            print("\nRevenue data:")
            print(revenue_df.head())
