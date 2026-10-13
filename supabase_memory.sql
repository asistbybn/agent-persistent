-- supabase_memory.sql
-- Jalankan 1x di Supabase SQL Editor (gratis)
-- Hasilnya: dapat MEMORY_URL + MEMORY_KEY untuk ditempel di device umum

create table if not exists memory (
  id bigint generated always as identity primary key,
  content text not null,
  created_at timestamptz default now()
);

-- Buka kunci baca-tulis via API key (untuk pemakaian pribadi):
alter table memory enable row level security;

drop policy if exists "allow_all" on memory;
create policy "allow_all" on memory
  for all using (true) with check (true);

-- Setelah ini ambil:
-- 1. Project Settings -> API -> Project URL  => MEMORY_URL = https://xxxx.supabase.co/rest/v1/memory
-- 2. Project Settings -> API -> anon public key => MEMORY_KEY = eyJh...
