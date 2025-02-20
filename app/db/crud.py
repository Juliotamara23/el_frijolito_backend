from sqlalchemy.orm import Session
from .models import ReporteNomina, QuincenaValor, ReporteNominaRecargo, ReporteNominaDescuento, ReporteNominaSubsidio
from .schemas import ReporteNominaCreate

def crear_reporte_nomina(db: Session, nomina_data: ReporteNominaCreate):
    """Crea un reporte de nómina y sus registros relacionados en una transacción."""
    try:
        nueva_nomina = ReporteNomina(
            empleado_id=nomina_data.empleado_id,
            fecha_inicio=nomina_data.fecha_inicio,
            fecha_fin=nomina_data.fecha_fin,
            total_pagado=nomina_data.total_pagado
        )
        db.add(nueva_nomina)
        db.flush()

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

        db.commit()
        db.refresh(nueva_nomina)
        return nueva_nomina

    except Exception as e:
        db.rollback()
        raise e
