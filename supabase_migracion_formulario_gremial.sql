-- Campos opcionales para el formulario especial de líderes gremiales
-- Ejecutar UNA VEZ en Supabase > SQL Editor

alter table public.relatoria_hallazgos
    add column if not exists tipo_hallazgo_gremial text,
    add column if not exists afectacion_gremial text,
    add column if not exists instrumento_gremial text;
