from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from .models import ReporteNomina, QuincenaValor, ReporteNominaRecargo, ReporteNominaDescuento, ReporteNominaSubsidio
from .schemas import ReporteNominaCreate, ReporteNominaUpdate
from fastapi import HTTPException
from uuid import UUID

async def crear_reporte_nomina(db: AsyncSession, nomina_data: ReporteNominaCreate):
    """Guarda en la base de datos una nómina ya calculada."""
    try:
        nueva_nomina = ReporteNomina(
            empleado_id=nomina_data.empleado_id,
            fecha_inicio=nomina_data.fecha_inicio,
            fecha_fin=nomina_data.fecha_fin,
            total_pagado=nomina_data.total_pagado  # Ya calculado
        )

        db.add(nueva_nomina)
        await db.flush()  # Asegurar que tiene ID antes de relacionar otros datos

        # Guardar detalles de quincena, recargos, descuentos y subsidios
        for valor in nomina_data.quincena_valores:
            db.add(QuincenaValor(
                reporte_nomina_id=nueva_nomina.id,
                tipo_recargo_id=valor.tipo_recargo_id,
                cantidad_dias=valor.cantidad_dias,
                valor_quincena=valor.valor_quincena
            ))

        for recargo_id in nomina_data.recargos:
            db.add(ReporteNominaRecargo(
                reporte_nomina_id=nueva_nomina.id,
                tipo_recargo_id=recargo_id
            ))

        for descuento_id in nomina_data.descuentos:
            db.add(ReporteNominaDescuento(
                reporte_nomina_id=nueva_nomina.id,
                tipo_descuento_id=descuento_id
            ))

        for subsidio_id in nomina_data.subsidios:
            db.add(ReporteNominaSubsidio(
                reporte_nomina_id=nueva_nomina.id,
                tipo_subsidio_id=subsidio_id
            ))

        await db.commit()
        await db.refresh(nueva_nomina)
        return nueva_nomina

    except Exception as e:
        await db.rollback()
        raise e

async def actualizar_reporte_nomina(db: AsyncSession, nomina_id: UUID, nomina_data: ReporteNominaUpdate):
    """Actualiza un reporte de nómina y sus registros relacionados en una transacción de forma asíncrona."""
    try:
        # Obtener la nómina existente
        result = await db.execute(
            select(ReporteNomina).where(ReporteNomina.id == nomina_id)
        )
        db_nomina = result.scalar_one_or_none()
        if not db_nomina:
            raise HTTPException(status_code=404, detail="Nómina no encontrada")

        # Actualizar campos básicos si se proporcionan
        if nomina_data.fecha_inicio is not None:
            db_nomina.fecha_inicio = nomina_data.fecha_inicio
        if nomina_data.fecha_fin is not None:
            db_nomina.fecha_fin = nomina_data.fecha_fin
        if nomina_data.total_pagado is not None:
            db_nomina.total_pagado = nomina_data.total_pagado

        # Actualizar quincena_valores si se proporcionan
        if nomina_data.quincena_valores is not None:
            await db.execute(
                delete(QuincenaValor).where(QuincenaValor.reporte_nomina_id == nomina_id)
            )
            for valor in nomina_data.quincena_valores:
                db.add(QuincenaValor(
                    reporte_nomina_id=nomina_id,
                    tipo_recargo_id=valor.tipo_recargo_id,
                    cantidad_dias=valor.cantidad_dias,
                    valor_quincena=valor.valor_quincena
                ))

        # Actualizar recargos si se proporcionan
        if nomina_data.recargos is not None:
            await db.execute(
                delete(ReporteNominaRecargo).where(ReporteNominaRecargo.reporte_nomina_id == nomina_id)
            )
            for recargo_id in nomina_data.recargos:
                db.add(ReporteNominaRecargo(
                    reporte_nomina_id=nomina_id,
                    tipo_recargo_id=recargo_id
                ))

        # Actualizar descuentos si se proporcionan
        if nomina_data.descuentos is not None:
            await db.execute(
                delete(ReporteNominaDescuento).where(ReporteNominaDescuento.reporte_nomina_id == nomina_id)
            )
            for descuento_id in nomina_data.descuentos:
                db.add(ReporteNominaDescuento(
                    reporte_nomina_id=nomina_id,
                    tipo_descuento_id=descuento_id
                ))

        # Actualizar subsidios si se proporcionan
        if nomina_data.subsidios is not None:
            await db.execute(
                delete(ReporteNominaSubsidio).where(ReporteNominaSubsidio.reporte_nomina_id == nomina_id)
            )
            if nomina_data.subsidios:
                for subsidio_id in nomina_data.subsidios:
                    db.add(ReporteNominaSubsidio(
                        reporte_nomina_id=nomina_id,
                        tipo_subsidio_id=subsidio_id
                    ))

        await db.commit()
        await db.refresh(db_nomina)
        return db_nomina

    except Exception as e:
        await db.rollback()
        raise e

async def eliminar_reporte_nomina(db: AsyncSession, nomina_id: UUID):
    """Elimina un reporte de nómina y sus registros relacionados en una transacción de forma asíncrona."""
    try:
        # Obtener la nómina existente
        result = await db.execute(
            select(ReporteNomina).where(ReporteNomina.id == nomina_id)
        )
        db_nomina = result.scalar_one_or_none()
        if not db_nomina:
            raise HTTPException(status_code=404, detail="Nómina no encontrada")

        # Eliminar registros relacionados
        await db.execute(delete(QuincenaValor).where(QuincenaValor.reporte_nomina_id == nomina_id))
        await db.execute(delete(ReporteNominaRecargo).where(ReporteNominaRecargo.reporte_nomina_id == nomina_id))
        await db.execute(delete(ReporteNominaDescuento).where(ReporteNominaDescuento.reporte_nomina_id == nomina_id))
        await db.execute(delete(ReporteNominaSubsidio).where(ReporteNominaSubsidio.reporte_nomina_id == nomina_id))

        # Eliminar la nómina
        await db.delete(db_nomina)
        await db.commit()

        return {"mensaje": "Nómina eliminada exitosamente", "nomina": db_nomina}

    except Exception as e:
        await db.rollback()
        raise e