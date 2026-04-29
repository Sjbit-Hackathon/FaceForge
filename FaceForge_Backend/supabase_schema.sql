create extension if not exists "pgcrypto";

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password_hash text not null,
  full_name text not null,
  badge_id text not null,
  role text not null default 'OFFICER',
  created_at timestamptz not null default now()
);

create table if not exists public.sessions (
  id uuid primary key default gen_random_uuid(),
  case_number text unique not null,
  title text not null,
  witness_name text,
  notes text,
  status text not null default 'active',
  owner_user_id uuid not null references public.users(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.versions (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.sessions(id) on delete cascade,
  version_label text not null default 'v3',
  parent_version_id uuid references public.versions(id) on delete set null,
  prompt text not null,
  features jsonb not null default '{}'::jsonb,
  image_path text not null,
  image_hash text not null,
  face_embedding jsonb,
  created_by uuid not null references public.users(id) on delete restrict,
  created_at timestamptz not null default now()
);

create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_user_id uuid not null references public.users(id) on delete cascade,
  action text not null,
  entity_type text not null,
  entity_id uuid,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_sessions_owner_user_id on public.sessions(owner_user_id);
create index if not exists idx_versions_session_id on public.versions(session_id);
create index if not exists idx_audit_logs_actor_user_id on public.audit_logs(actor_user_id);
create index if not exists idx_audit_logs_created_at on public.audit_logs(created_at desc);

alter table public.users enable row level security;
alter table public.sessions enable row level security;
alter table public.versions enable row level security;
alter table public.audit_logs enable row level security;

create policy "service role users full access"
on public.users for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');

create policy "service role sessions full access"
on public.sessions for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');

create policy "service role versions full access"
on public.versions for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');

create policy "service role audit logs full access"
on public.audit_logs for all
using (auth.role() = 'service_role')
with check (auth.role() = 'service_role');
