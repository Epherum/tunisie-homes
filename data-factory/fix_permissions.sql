-- Fix for "permission denied for schema public" error
-- Run this in the Supabase SQL Editor

-- 1. Grant usage on the public schema
GRANT USAGE ON SCHEMA public TO anon, authenticated;

-- 2. Grant select permission on the listings table
GRANT SELECT ON public.listings TO anon, authenticated;

-- 3. (Optional) If you have RLS enabled, ensure there is a policy
-- ALTER TABLE public.listings ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow public read access" ON public.listings FOR SELECT USING (true);
