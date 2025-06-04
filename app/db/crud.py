from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.services.payroll import calcular_nomina
from .models import ReporteNomina, QuincenaValor, ReporteNominaRecargo, ReporteNominaDescuento, ReporteNominaSubsidio, Empleado
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
        result = await db.execute(select(ReporteNomina).where(ReporteNomina.id == nomina_id))
        db_nomina = result.scalar_one_or_none()
        if not db_nomina:
            raise HTTPException(status_code=404, detail="Nómina no encontrada")

        # Verificar si se necesita recalcular la nómina
        recalcular = (
            nomina_data.fecha_inicio is not None or
            nomina_data.fecha_fin is not None or
            nomina_data.quincena_valores is not None or
            nomina_data.recargos is not None or
            nomina_data.descuentos is not None or
            nomina_data.subsidios is not None
        )

        # Si hay cambios estructurales, recalculamos la nómina
        if recalcular:
            nomina_data = await calcular_nomina(db, nomina_data)

        # Actualizar solo los campos que han cambiado
        cambios = False

        if nomina_data.empleado_id is not None and db_nomina.empleado_id != nomina_data.empleado_id:
            db_nomina.empleado_id = nomina_data.empleado_id
            cambios = True
        if nomina_data.fecha_inicio is not None and db_nomina.fecha_inicio != nomina_data.fecha_inicio:
            db_nomina.fecha_inicio = nomina_data.fecha_inicio
            cambios = True
        if nomina_data.fecha_fin is not None and db_nomina.fecha_fin != nomina_data.fecha_fin:
            db_nomina.fecha_fin = nomina_data.fecha_fin
            cambios = True
        if nomina_data.total_pagado is not None and db_nomina.total_pagado != nomina_data.total_pagado:
            db_nomina.total_pagado = nomina_data.total_pagado
            cambios = True

        # Optimizar actualización de quincena_valores
        if nomina_data.quincena_valores is not None:
            result = await db.execute(select(QuincenaValor).where(QuincenaValor.reporte_nomina_id == nomina_id))
            quincena_existente = {qv.tipo_recargo_id: qv for qv in result.scalars().all()}
            quincena_nueva = {qv.tipo_recargo_id: qv for qv in nomina_data.quincena_valores}

            # Identificar cambios
            actualizar, agregar = [], []
            for tipo_recargo_id, qv in quincena_nueva.items():
                if tipo_recargo_id in quincena_existente:
                    if (
                        quincena_existente[tipo_recargo_id].cantidad_dias != qv.cantidad_dias or
                        quincena_existente[tipo_recargo_id].valor_quincena != qv.valor_quincena
                    ):
                        # Actualizar individualmente cada registro
                        await db.execute(
                            update(QuincenaValor)
                            .where(
                                QuincenaValor.reporte_nomina_id == nomina_id,
                                QuincenaValor.tipo_recargo_id == tipo_recargo_id
                            )
                            .values(
                                cantidad_dias=qv.cantidad_dias,
                                valor_quincena=qv.valor_quincena
                            )
                        )
                        cambios = True
                else:
                    agregar.append(QuincenaValor(
                        reporte_nomina_id=nomina_id,
                        tipo_recargo_id=qv.tipo_recargo_id,
                        cantidad_dias=qv.cantidad_dias,
                        valor_quincena=qv.valor_quincena
                    ))

            # Agregar nuevos registros
            if agregar:
                db.add_all(agregar)
                cambios = True

        # Optimizar actualización de recargos
        if nomina_data.recargos is not None:
            result = await db.execute(select(ReporteNominaRecargo).where(ReporteNominaRecargo.reporte_nomina_id == nomina_id))
            recargos_existentes = {r.tipo_recargo_id for r in result.scalars().all()}
            recargos_nuevos = set(nomina_data.recargos)

            agregar = recargos_nuevos - recargos_existentes
            eliminar = recargos_existentes - recargos_nuevos

            if eliminar:
                await db.execute(
                    delete(ReporteNominaRecargo).where(
                        ReporteNominaRecargo.reporte_nomina_id == nomina_id,
                        ReporteNominaRecargo.tipo_recargo_id.in_(eliminar)
                    )
                )
                cambios = True

            if agregar:
                db.add_all([
                    ReporteNominaRecargo(reporte_nomina_id=nomina_id, tipo_recargo_id=recargo_id)
                    for recargo_id in agregar
                ])
                cambios = True

        # Optimizar actualización de descuentos
        if nomina_data.descuentos is not None:
            result = await db.execute(select(ReporteNominaDescuento).where(ReporteNominaDescuento.reporte_nomina_id == nomina_id))
            descuentos_existentes = {d.tipo_descuento_id for d in result.scalars().all()}
            descuentos_nuevos = set(nomina_data.descuentos)

            agregar = descuentos_nuevos - descuentos_existentes
            eliminar = descuentos_existentes - descuentos_nuevos

            if eliminar:
                await db.execute(
                    delete(ReporteNominaDescuento).where(
                        ReporteNominaDescuento.reporte_nomina_id == nomina_id,
                        ReporteNominaDescuento.tipo_descuento_id.in_(eliminar)
                    )
                )
                cambios = True

            if agregar:
                db.add_all([
                    ReporteNominaDescuento(reporte_nomina_id=nomina_id, tipo_descuento_id=desc_id)
                    for desc_id in agregar
                ])
                cambios = True

        # Optimizar actualización de subsidios
        if nomina_data.subsidios is not None:
            result = await db.execute(select(ReporteNominaSubsidio).where(ReporteNominaSubsidio.reporte_nomina_id == nomina_id))
            subsidios_existentes = {s.tipo_subsidio_id for s in result.scalars().all()}
            subsidios_nuevos = set(nomina_data.subsidios)

            agregar = subsidios_nuevos - subsidios_existentes
            eliminar = subsidios_existentes - subsidios_nuevos

            if eliminar:
                await db.execute(
                    delete(ReporteNominaSubsidio).where(
                        ReporteNominaSubsidio.reporte_nomina_id == nomina_id,
                        ReporteNominaSubsidio.tipo_subsidio_id.in_(eliminar)
                    )
                )
                cambios = True

            if agregar:
                db.add_all([
                    ReporteNominaSubsidio(reporte_nomina_id=nomina_id, tipo_subsidio_id=sub_id)
                    for sub_id in agregar
                ])
                cambios = True

        # Si hubo cambios, commit y refrescar
        if cambios:
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