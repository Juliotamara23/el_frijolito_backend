import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (
    Empleado, ConfigSalario, TipoRecargo, 
    TipoDescuento, TipoSubsidio
)
from app.services.payroll import calcular_nomina
from app.db.schemas import ReporteNominaCreate, QuincenaValorCreate
from app.db.crud import crear_reporte_nomina

@pytest.fixture
async def test_data(db_session: AsyncSession):
    """Create test data"""
    empleado = Empleado(
        id=uuid4(),
        cedula="1234567890",
        nombres="Test",
        apellidos="Usuario",
        telefono="1234567890",
        puesto_trabajo="Analista",
        salario_base=Decimal("2000000.00")
    )
    
    config = ConfigSalario(
        año="2024",
        salario_minimo=Decimal("1300000.00"),
        horas_semana=48,
        horas_mes=192,
        valor_hora=Decimal("5416.67"),
        horas_salario=8
    )
    
    recargo_ordinario = TipoRecargo(
        id=1,
        tipo_hora="ORDINARIA",
        porcentaje=Decimal("0.00"),
        valor_hora=Decimal("5416.67"),
        detalle="Hora ordinaria"
    )
    
    recargo_nocturno = TipoRecargo(
        id=2,
        tipo_hora="NOCTURNA",
        porcentaje=Decimal("0.35"),
        valor_hora=Decimal("7312.50"),
        detalle="Hora nocturna"
    )
    
    descuento_salud = TipoDescuento(
        id=1,
        tipo="SALUD",
        valor=Decimal("0.04")
    )
    
    descuento_pension = TipoDescuento(
        id=2,
        tipo="PENSION",
        valor=Decimal("0.04")
    )
    
    subsidio_transporte = TipoSubsidio(
        id=1,
        tipo="TRANSPORTE",
        valor=Decimal("140606.00")
    )
    
    db_session.add_all([
        empleado, config, recargo_ordinario, recargo_nocturno,
        descuento_salud, descuento_pension, subsidio_transporte
    ])
    await db_session.commit()
    await db_session.refresh(empleado)
    
    yield {
        "empleado_id": empleado.id,
        "config": config,
        "recargos": [recargo_ordinario, recargo_nocturno],
        "descuentos": [descuento_salud, descuento_pension],
        "subsidio": subsidio_transporte
    }

    # Cleanup
    await db_session.rollback()

@pytest.mark.asyncio
async def test_calculo_nomina_basica(db_session: AsyncSession, test_data):
    """Test basic payroll calculation"""
    # Create test data
    nomina_data = ReporteNominaCreate(
        empleado_id=test_data["empleado_id"],
        fecha_inicio=date(2024, 2, 1),
        fecha_fin=date(2024, 2, 15),
        quincena_valores=[
            QuincenaValorCreate(
                tipo_recargo_id=1,
                cantidad_dias=15,
                valor_quincena=Decimal("0")
            )
        ],
        recargos=[1],
        descuentos=[1, 2],
        subsidios=[1]
    )
    
    # Calculate and save
    nomina_calculada = await calcular_nomina(db_session, nomina_data)
    reporte_guardado = await crear_reporte_nomina(db_session, nomina_calculada)
    
    assert reporte_guardado is not None
    assert reporte_guardado.total_pagado > 0

@pytest.mark.asyncio
async def test_calculo_nomina_con_recargos(db_session: AsyncSession, test_data):
    """Prueba cálculo de nómina con horas ordinarias y nocturnas"""
    print("\n=== Test Cálculo Nómina con recargos ===")

    nomina_data = ReporteNominaCreate(
        empleado_id=test_data["empleado_id"],
        fecha_inicio=date(2024, 2, 1),
        fecha_fin=date(2024, 2, 15),
        quincena_valores=[
            QuincenaValorCreate(
                tipo_recargo_id=1,
                cantidad_dias=10,
                valor_quincena=Decimal("0.00")
            ),
            QuincenaValorCreate(
                tipo_recargo_id=2,
                cantidad_dias=5,
                valor_quincena=Decimal("0.00")
            )
        ],
        recargos=[1, 2],
        descuentos=[1, 2],
        subsidios=[1]
    )
    
    result = await calcular_nomina(db_session, nomina_data)
    
    valor_hora_ordinaria = Decimal("6189.13")
    valor_hora_nocturna = Decimal("8355.33")
    dias_ordinarios = Decimal("10")
    dias_nocturnos = Decimal("5")
    horas = Decimal("8")
    subsidio = Decimal("100000.00")
    porcentaje_descuento = Decimal("0.08")

    valor_ordinario = valor_hora_ordinaria * dias_ordinarios * horas
    valor_nocturno = valor_hora_nocturna * dias_nocturnos * horas
    total_devengado = valor_ordinario + valor_nocturno + subsidio
    descuentos = total_devengado * porcentaje_descuento
    expected_total = total_devengado - descuentos
    
    assert result.total_pagado == pytest.approx(expected_total, rel=Decimal("0.01"))

    # Guardar en base de datos
    from app.db.crud import crear_reporte_nomina
    reporte_guardado = await crear_reporte_nomina(db_session, nomina_data)
    
    # Verificar que se guardó correctamente
    from sqlalchemy import select
    from app.db.models import ReporteNomina
    
    result = await db_session.execute(
        select(ReporteNomina).where(ReporteNomina.id == reporte_guardado.id)
    )
    nomina_guardada = result.scalar_one_or_none()
    
    assert nomina_guardada is not None
    assert nomina_guardada.total_pagado == pytest.approx(expected_total, rel=Decimal("0.01"))
    
    # Verificar detalles guardados
    assert len(nomina_guardada.quincena_valores) == 2  # Debe tener dos registros
    assert len(nomina_guardada.recargos) == 2
    assert len(nomina_guardada.descuentos) == 2
    assert len(nomina_guardada.subsidios) == 1

@pytest.mark.asyncio
async def test_calculo_nomina_sin_subsidio(db_session: AsyncSession, test_data):
    """Prueba cálculo de nómina sin subsidio de transporte"""
    print("\n=== Test Cálculo Nómina sin subsidio ===")

    nomina_data = ReporteNominaCreate(
        empleado_id=test_data["empleado_id"],
        fecha_inicio=date(2024, 2, 1),
        fecha_fin=date(2024, 2, 15),
        quincena_valores=[
            QuincenaValorCreate(
                tipo_recargo_id=1,
                cantidad_dias=15,
                valor_quincena=Decimal("0.00")
            )
        ],
        recargos=[1],
        descuentos=[1, 2],
        subsidios=[]
    )
    
    result = await calcular_nomina(db_session, nomina_data)
    
    valor_hora = Decimal("6189.13")
    dias = Decimal("15")
    horas = Decimal("8")
    porcentaje_descuento = Decimal("0.08")

    valor_ordinario = valor_hora * dias * horas
    descuentos = valor_ordinario * porcentaje_descuento
    expected_total = valor_ordinario - descuentos
    
    assert result.total_pagado == pytest.approx(expected_total, rel=Decimal("0.01"))

    # Guardar en base de datos
    from app.db.crud import crear_reporte_nomina
    reporte_guardado = await crear_reporte_nomina(db_session, nomina_data)
    
    # Verificar que se guardó correctamente
    from sqlalchemy import select
    from app.db.models import ReporteNomina
    
    result = await db_session.execute(
        select(ReporteNomina).where(ReporteNomina.id == reporte_guardado.id)
    )
    nomina_guardada = result.scalar_one_or_none()
    
    assert nomina_guardada is not None
    assert nomina_guardada.total_pagado == pytest.approx(expected_total, rel=Decimal("0.01"))
    
    # Verificar detalles guardados
    assert len(nomina_guardada.quincena_valores) == 1
    assert len(nomina_guardada.recargos) == 1
    assert len(nomina_guardada.descuentos) == 2
    assert len(nomina_guardada.subsidios) == 0