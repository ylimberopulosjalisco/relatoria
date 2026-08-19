-- Migración para vincular cada hallazgo con la guía de moderación
-- Ejecutar UNA VEZ en Supabase > SQL Editor.

alter table public.relatoria_hallazgos
    add column if not exists tipo_pregunta text,
    add column if not exists pregunta_referencia text;

comment on column public.relatoria_hallazgos.tipo_pregunta
    is 'Tipo de intervención: detonadora, central, cierre o seguimiento/repregunta';

comment on column public.relatoria_hallazgos.pregunta_referencia
    is 'Pregunta de la guía de moderación a la que se vincula el hallazgo';
