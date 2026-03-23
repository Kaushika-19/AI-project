from supabase import create_client

url = "https://snodirqiucxpcsdculmf.supabase.co"
key = "sbp_1ba184f8824b490a0f67b4c340bba3ad10958509"

supabase = create_client(url, key)

print("Connected successfully")