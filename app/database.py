from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Cliente público (para operações normais)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cliente admin (para verificar tokens)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)