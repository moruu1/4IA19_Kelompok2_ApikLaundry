from supabase import create_client, Client
from datetime import datetime
from config import SUPABASE_URL, SUPABASE_KEY

def fetch_financial_data():
    """
    Fetch financial data from Supabase
    Returns: list of dicts with financial data
    """
    try:
        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Fetch financial data
        response = supabase.table('financials').select('*').execute()
        data = response.data
        
        if not data:
            print("No data found in financials table")
            return None
        
        # Process data: Convert strings to datetime objects for sorting
        for item in data:
            try:
                # Assuming 'tanggal' is in ISO format or YYYY-MM-DD
                if isinstance(item['tanggal'], str):
                    # Handle typically date string formats if needed, or rely on isoformat
                    # Truncate time part if it exists for date-only grouping logic later
                    date_str = item['tanggal'].split('T')[0]
                    item['tanggal_obj'] = datetime.strptime(date_str, '%Y-%m-%d').date()
                else:
                    item['tanggal_obj'] = None
            except Exception as e:
                print(f"Error parsing date for item {item}: {e}")
                item['tanggal_obj'] = None

        # Filter out items with invalid dates if necessary
        data = [x for x in data if x['tanggal_obj'] is not None]

        # Sort by date
        data.sort(key=lambda x: x['tanggal_obj'])
        
        return data
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_revenue_data():
    """
    Get only Pemasukan (revenue) data
    Returns: list of dicts with revenue data aggregated by date
    [{'date': date_obj, 'revenue': float}, ...]
    """
    data = fetch_financial_data()
    
    if data is None:
        return None
    
    # Filter only Pemasukan (revenue)
    revenue_data = [x for x in data if x.get('tipe') == 'Pemasukan']
    
    # Group by date and sum the revenue
    revenue_by_date = {}
    for item in revenue_data:
        date_key = item['tanggal_obj']
        amount = float(item.get('jumlah', 0))
        
        if date_key in revenue_by_date:
            revenue_by_date[date_key] += amount
        else:
            revenue_by_date[date_key] = amount
    
    # Convert to list of dicts and sort
    result = []
    for date_key, total in revenue_by_date.items():
        result.append({
            'date': date_key,
            'revenue': total
        })
    
    result.sort(key=lambda x: x['date'])
    
    return result

if __name__ == "__main__":
    # Test the functions
    print("Testing data fetch from Supabase...\n")
    
    # Fetch all financial data
    data = fetch_financial_data()
    
    if data is not None:
        print("\n" + "="*50)
        print(f"Sample data (first 5): {data[:5]}")
        
        print("\n" + "="*50)
        # Get revenue data
        revenue_data = get_revenue_data()
        
        if revenue_data is not None:
            print("\nRevenue data (first 5):")
            print(revenue_data[:5])

