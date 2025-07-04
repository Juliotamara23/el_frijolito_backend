from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID

# Función para obtener todos los reportes de nóminas
async def obtener_reporte_nominas(db: AsyncSession):
    query = text("""
    SELECT
        rn.id,
        rn.empleado_id,
        e.cedula,
        e.nombres,
        e.apellidos,
        e.telefono,
        e.puesto_trabajo,
        rn.fecha_inicio,
        rn.fecha_fin,

        -- Descuentos
        COALESCE(
            STRING_AGG(DISTINCT td.tipo, '\n') 
            FILTER (WHERE td.tipo IS NOT NULL), 'Sin descuentos'
        ) AS descuentos_aplicados,

        -- Subsidios
        COALESCE(
            STRING_AGG(DISTINCT ts.tipo, '\n') 
            FILTER (WHERE ts.tipo IS NOT NULL), 'Sin subsidios'
        ) AS subsidios_aplicados,

        -- Recargos y Valores de Quincena
        COALESCE(
            STRING_AGG(DISTINCT tr.tipo_hora || ' ' || qv.cantidad_dias::text || ' días $ ' || qv.valor_quincena::text, '\n') 
            FILTER (WHERE tr.tipo_hora IS NOT NULL), 'Sin recargos'
        ) AS recargos_y_valores,

        rn.total_pagado

    FROM reportes_nominas rn
    INNER JOIN empleados e ON e.id = rn.empleado_id
    LEFT JOIN reportes_nominas_descuentos rnd ON rn.id = rnd.reporte_nomina_id
    LEFT JOIN tipos_descuentos td ON rnd.tipo_descuento_id = td.id
    LEFT JOIN reportes_nominas_recargos rnr ON rn.id = rnr.reporte_nomina_id
    LEFT JOIN tipos_recargos tr ON rnr.tipo_recargo_id = tr.id
    LEFT JOIN quincena_valores qv ON rn.id = qv.reporte_nomina_id AND tr.id = qv.tipo_recargo_id
    LEFT JOIN reportes_nominas_subsidios rns ON rn.id = rns.reporte_nomina_id
    LEFT JOIN tipos_subsidios ts ON rns.tipo_subsidio_id = ts.id

    GROUP BY 
        rn.id, rn.empleado_id, e.cedula, e.nombres, e.apellidos,
        e.telefono, e.puesto_trabajo, rn.fecha_inicio, rn.fecha_fin,
        rn.total_pagado

    ORDER BY rn.fecha_inicio DESC;
    """)

    result = await db.execute(query)
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]

# Función para obtener un reporte de nómina por su ID
async def obtener_reporte_nomina(db: AsyncSession, nomina_id: UUID):
    query = text("""
SELECT
    rn.id,
    rn.empleado_id,
    e.cedula,
    e.nombres,
    e.apellidos,
    e.telefono,
    e.puesto_trabajo,
    rn.fecha_inicio,
    rn.fecha_fin,
    rn.total_pagado,
    
    -- Array de objetos quincena_valores con tipo_recargo_id
    COALESCE(
        JSONB_AGG(
            DISTINCT jsonb_build_object(
                'tipo_recargo_id', qv.tipo_recargo_id,
                'cantidad_dias', qv.cantidad_dias,
                'valor_quincena', qv.valor_quincena
            )
        ) FILTER (WHERE qv.tipo_recargo_id IS NOT NULL), '[]'::jsonb
    ) AS quincena_valores,

    -- Lista de IDs de recargos aplicados
    COALESCE(
        JSONB_AGG(DISTINCT tr.id) FILTER (WHERE tr.id IS NOT NULL), '[]'::jsonb
    ) AS recargos,

    -- Lista de IDs de descuentos aplicados
    COALESCE(
        JSONB_AGG(DISTINCT td.id) FILTER (WHERE td.id IS NOT NULL), '[]'::jsonb
    ) AS descuentos,

    -- Lista de IDs de subsidios aplicados
    COALESCE(
        JSONB_AGG(DISTINCT ts.id) FILTER (WHERE ts.id IS NOT NULL), '[]'::jsonb
    ) AS subsidios

FROM reportes_nominas rn
INNER JOIN empleados e ON e.id = rn.empleado_id
LEFT JOIN reportes_nominas_descuentos rnd ON rn.id = rnd.reporte_nomina_id
LEFT JOIN tipos_descuentos td ON rnd.tipo_descuento_id = td.id
LEFT JOIN reportes_nominas_recargos rnr ON rn.id = rnr.reporte_nomina_id
LEFT JOIN tipos_recargos tr ON rnr.tipo_recargo_id = tr.id
LEFT JOIN quincena_valores qv ON rn.id = qv.reporte_nomina_id AND tr.id = qv.tipo_recargo_id
LEFT JOIN reportes_nominas_subsidios rns ON rn.id = rns.reporte_nomina_id
LEFT JOIN tipos_subsidios ts ON rns.tipo_subsidio_id = ts.id
WHERE rn.id = :nomina_id
GROUP BY 
    rn.id, rn.empleado_id, e.cedula, e.nombres, e.apellidos,
    e.telefono, e.puesto_trabajo, rn.fecha_inicio, rn.fecha_fin,
    rn.total_pagado;
    """)
    
    result = await db.execute(query, {"nomina_id": nomina_id})
    row = result.fetchone()
    if row is None:
        return None
    return dict(row._mapping)
