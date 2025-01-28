from supabase import create_client, Client
import os

# Define the Supabase URL and Key
supabase_url = "https://qnbvpygecpodwfprshez.supabase.co"
supabase_key = os.getenv("SUPABASE_KEY")

# Create the Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Example usage: Fetch data from a table
def fetch_data():
    response = supabase.table("your_table_name").select("*").execute()
    if response.get("data"):
        return response.get("data")
    else:
        print(response.get("error"))

# Example: Fetch and print data
if __name__ == "__main__":
    data = fetch_data()
    if data:
        print(data)

supabase_client = supabase
