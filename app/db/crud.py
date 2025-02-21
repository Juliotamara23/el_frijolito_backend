from sqlalchemy.orm import Session
from .models import ReporteNomina, QuincenaValor, ReporteNominaRecargo, ReporteNominaDescuento, ReporteNominaSubsidio
from .schemas import ReporteNominaCreate, ReporteNominaUpdate
from fastapi import HTTPException
from uuid import UUID

def crear_reporte_nomina(db: Session, nomina_data: ReporteNominaCreate):
    """Crea un reporte de nómina y sus registros relacionados en una transacción."""
    try:
        nueva_nomina = ReporteNomina(
            empleado_id = nomina_data.empleado_id,
            fecha_inicio = nomina_data.fecha_inicio,
            fecha_fin = nomina_data.fecha_fin,
            total_pagado = nomina_data.total_pagado
        )
        db.add(nueva_nomina)
        db.flush()

        # Agregar quincena_valores
        for valor in nomina_data.quincena_valores:
            db.add(QuincenaValor(
                reporte_nomina_id = nueva_nomina.id,
                tipo_recargo_id = valor.tipo_recargo_id,
                cantidad_dias = valor.cantidad_dias,
                valor_quincena = valor.valor_quincena
            ))
        
        # Agregar recargos
        for recargo_id in nomina_data.recargos:
            db.add(ReporteNominaRecargo(
                reporte_nomina_id = nueva_nomina.id,
                tipo_recargo_id = recargo_id
            ))

        # Agregar descuentos
        for descuento_id in nomina_data.descuentos:
            db.add(ReporteNominaDescuento(
                reporte_nomina_id = nueva_nomina.id,
                tipo_descuento_id = descuento_id
            ))

        # Agregar subsidios solo si existen
        if nomina_data.subsidios:
            for subsidio_id in nomina_data.subsidios:
                db.add(ReporteNominaSubsidio(
                    reporte_nomina_id = nueva_nomina.id,
                    tipo_subsidio_id = subsidio_id
                ))

        db.commit()
        db.refresh(nueva_nomina)
        return nueva_nomina

    except Exception as e:
        db.rollback()
        raise e

def actualizar_reporte_nomina(db: Session, nomina_id: UUID, nomina_data: ReporteNominaUpdate):
    """Actualiza un reporte de nómina y sus registros relacionados en una transacción."""
    try:
        # Obtener la nómina existente
        db_nomina = db.query(ReporteNomina).filter(ReporteNomina.id == nomina_id).first()
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
            # Eliminar valores existentes
            db.query(QuincenaValor).filter(QuincenaValor.reporte_nomina_id == nomina_id).delete()
            # Agregar nuevos valores
            for valor in nomina_data.quincena_valores:
                db.add(QuincenaValor(
                    reporte_nomina_id = nomina_id,
                    tipo_recargo_id = valor.tipo_recargo_id,
                    cantidad_dias = valor.cantidad_dias,
                    valor_quincena = valor.valor_quincena
                ))

        # Actualizar recargos si se proporcionan
        if nomina_data.recargos is not None:
            # Eliminar recargos existentes
            db.query(ReporteNominaRecargo).filter(ReporteNominaRecargo.reporte_nomina_id == nomina_id).delete()
            # Agregar nuevos recargos
            for recargo_id in nomina_data.recargos:
                db.add(ReporteNominaRecargo(
                    reporte_nomina_id = nomina_id,
                    tipo_recargo_id = recargo_id
                ))

        # Actualizar descuentos si se proporcionan
        if nomina_data.descuentos is not None:
            # Eliminar descuentos existentes
            db.query(ReporteNominaDescuento).filter(ReporteNominaDescuento.reporte_nomina_id == nomina_id).delete()
            # Agregar nuevos descuentos
            for descuento_id in nomina_data.descuentos:
                db.add(ReporteNominaDescuento(
                    reporte_nomina_id = nomina_id,
                    tipo_descuento_id = descuento_id
                ))

        # Actualizar subsidios si se proporcionan
        if nomina_data.subsidios is not None:
            # Eliminar subsidios existentes
            db.query(ReporteNominaSubsidio).filter(
                ReporteNominaSubsidio.reporte_nomina_id == nomina_id
            ).delete()
            # Agregar nuevos subsidios si no esta vacio
            if nomina_data.subsidios:
                for subsidio_id in nomina_data.subsidios:
                    db.add(ReporteNominaSubsidio(
                        reporte_nomina_id = nomina_id,
                        tipo_subsidio_id = subsidio_id
                    ))

        db.commit()
        db.refresh(db_nomina)
        return db_nomina

    except Exception as e:
        db.rollback()
        raise e
    
def eliminar_reporte_nomina(db: Session, nomina_id: UUID):
    """Elimina un reporte de nómina y sus registros relacionados en una transacción."""
    try:
        # Obtener la nómina existente
        db_nomina = db.query(ReporteNomina).filter(ReporteNomina.id == nomina_id).first()
        if not db_nomina:
            raise HTTPException(status_code=404, detail="Nómina no encontrada")

        # Eliminar registros relacionados
        db.query(QuincenaValor).filter(QuincenaValor.reporte_nomina_id == nomina_id).delete()
        db.query(ReporteNominaRecargo).filter(ReporteNominaRecargo.reporte_nomina_id == nomina_id).delete()
        db.query(ReporteNominaDescuento).filter(ReporteNominaDescuento.reporte_nomina_id == nomina_id).delete()
        db.query(ReporteNominaSubsidio).filter(ReporteNominaSubsidio.reporte_nomina_id == nomina_id).delete()

        # Eliminar la nómina
        db.delete(db_nomina)
        db.commit()

        return {"message": "Nómina eliminada exitosamente", "nomina": db_nomina}

    except Exception as e:
        db.rollback()
        raise e