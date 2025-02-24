from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.models import (
    Empleado, 
    ConfigSalario, 
    TipoRecargo, 
    TipoSubsidio, 
    TipoDescuento
)
from ..db.schemas import ReporteNominaCreate
from decimal import Decimal
from fastapi import HTTPException

async def calcular_nomina(db: AsyncSession, nomina: ReporteNominaCreate):
    """Calcula la nómina del empleado incluyendo recargos, subsidios y descuentos."""
    try:
        # 1. Obtener datos del empleado
        result = await db.execute(
            select(Empleado).where(Empleado.id == nomina.empleado_id)
        )
        empleado = result.scalar_one_or_none()
        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        # 2. Obtener configuración de salario vigente
        result = await db.execute(
            select(ConfigSalario).order_by(ConfigSalario.año.desc())
        )
        config_salario = result.scalar_one_or_none()
        if not config_salario:
            raise HTTPException(status_code=404, detail="No hay configuración de salario vigente")

        # 3. Validar fechas
        if nomina.fecha_inicio > nomina.fecha_fin:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser mayor que la fecha de fin"
            )

        # 4. Obtener tipos de recargos
        recargos_result = await db.execute(select(TipoRecargo))
        recargos = {r.id: r for r in recargos_result.scalars().all()}

        # 5. Calcular total por quincena
        total_devengado = Decimal('0')
        for valor in nomina.quincena_valores:
            recargo = recargos.get(valor.tipo_recargo_id)
            if not recargo:
                raise HTTPException(
                    status_code=404,
                    detail=f"Tipo de recargo {valor.tipo_recargo_id} no encontrado"
                )

            if recargo.tipo_hora == 'ORDINARIA':
                # Cálculo de horas ordinarias
                valor_calculado = (
                    recargo.valor_hora * 
                    valor.cantidad_dias * 
                    config_salario.horas_salario
                )
            elif recargo.tipo_hora in ['EXTRA_DIURNA', 'EXTRA_NOCTURNA', 'EXTRA_DOMINICAL_DIURNA', 'EXTRA_DOMINICAL_NOCTURNA']:
                # Cálculo de horas extras
                valor_calculado = recargo.valor_hora * valor.cantidad_dias
            elif recargo.tipo_hora == 'NOCTURNA':
                # Cálculo de recargo nocturno
                valor_calculado = (
                    recargo.valor_hora * 
                    config_salario.horas_salario * 
                    valor.cantidad_dias
                )
            else:
                # Cálculo de otros recargos (dominicales y dominicales nocturnos)
                valor_calculado = recargo.valor_hora * valor.cantidad_dias

            valor.valor_quincena = valor_calculado
            total_devengado += valor_calculado

        # 6. Aplicar subsidio de transporte si corresponde
        if nomina.subsidios:
            subsidios_result = await db.execute(select(TipoSubsidio))
            subsidios = {s.id: s for s in subsidios_result.scalars().all()}
            
            for subsidio_id in nomina.subsidios:
                subsidio = subsidios.get(subsidio_id)
                if subsidio:
                    total_devengado += subsidio.valor

        # 7. Aplicar descuentos (salud y pensión)
        descuentos_result = await db.execute(select(TipoDescuento))
        descuentos = {d.id: d for d in descuentos_result.scalars().all()}
        
        total_descuentos = Decimal('0')
        for descuento_id in nomina.descuentos:
            descuento = descuentos.get(descuento_id)
            if descuento:
                total_descuentos += total_devengado * descuento.valor

        # 8. Calcular total final
        nomina.total_pagado = total_devengado - total_descuentos

        # 9. Validaciones finales
        if nomina.total_pagado < 0:
            raise HTTPException(
                status_code=400,
                detail="El total a pagar no puede ser negativo"
            )

        return nomina

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))