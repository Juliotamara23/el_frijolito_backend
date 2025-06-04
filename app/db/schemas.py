from pydantic import BaseModel, condecimal, Field, constr, conint
from typing import Optional, Annotated, List
from decimal import Decimal
from datetime import date
from uuid import UUID

# Esquema para la tabla empleados
class EmpleadoBase(BaseModel):
    cedula: Annotated[str, Field(min_length=10, max_length=10, pattern=r'^\d{10}$')]  # Validación de longitud y formato
    nombres: Annotated[str, Field(min_length=1, max_length=100)]
    apellidos: Annotated[str, Field(min_length=1, max_length=100)]
    telefono: Optional[Annotated[str, Field(min_length=7, max_length=15, pattern=r'^\+?\d{7,15}$')]] = None  # Validación de formato
    puesto_trabajo: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    salario_base: Annotated[Decimal, Field(max_digits=20, decimal_places=2, ge=0)]  # Validación de rango

class EmpleadoCreate(EmpleadoBase):
    pass

class EmpleadoUpdate(EmpleadoBase):
    pass

class Empleado(EmpleadoBase):
    id: UUID

    class Config:
        from_attributes: True

# Esquema para la tabla config_salario
class ConfigSalarioBase(BaseModel):
    año: Annotated[int, Field(gt=0)]  # Validación de formato de año
    salario_minimo: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=False, ge=0)]  # Validación de rango
    horas_semana: Annotated[int, Field(ge=0, le=168)]  # Validación de rango (máximo 168 horas en una semana)
    horas_mes: Annotated[int, Field(ge=0, le=744)]  # Validación de rango (máximo 744 horas en un mes)
    valor_hora: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=False, ge=0)]  # Validación de rango
    horas_salario: Annotated[int, Field(ge=0, le=168)]  # Validación de rango (máximo 8 horas diarias)

class ConfigSalarioCreate(ConfigSalarioBase):
    pass

class ConfigSalarioUpdate(ConfigSalarioBase):
    pass

class ConfigSalario(ConfigSalarioBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla tipo_recargos
class TipoRecargoBase(BaseModel):
    tipo_hora: Annotated[str, constr(min_length=1, max_length=100)]
    porcentaje: Annotated[Decimal, Field(max_digits=5, decimal_places=4, strict=False, ge=0, le=2)]  # Validación de rango (0-1)
    valor_hora: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=False, ge=0)]  # Validación de rango
    detalle: Optional[Annotated[str, constr(max_length=255)]] = None

class TipoRecargoCreate(TipoRecargoBase):
    pass

class TipoRecargo(TipoRecargoBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla tipo_subsidios
class TipoSubsidioBase(BaseModel):
    tipo: Annotated[str, constr(min_length=1, max_length=100)]
    valor: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=False, ge=0)]  # Validación de rango

class TipoSubsidioCreate(TipoSubsidioBase):
    pass

class TipoSubsidio(TipoSubsidioBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla tipo_descuentos
class TipoDescuentoBase(BaseModel):
    tipo: Annotated[str, constr(min_length=1, max_length=100)]
    valor: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=False, ge=0)]  # Validación de rango

class TipoDescuentoCreate(TipoDescuentoBase):
    pass

class TipoDescuentoUpdate(TipoDescuentoBase):
    pass

class TipoDescuento(TipoDescuentoBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla quincena_valores
class QuincenaValorBase(BaseModel):
    tipo_recargo_id: int
    cantidad_dias: Annotated[int, conint(ge=0, le=31)]  # Validación de rango (máximo 31 días en un mes)
    valor_quincena: Optional[Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=False, ge=0)]] = None  # Validación de rango

class QuincenaValorCreate(QuincenaValorBase):
    pass

class QuincenaValor(QuincenaValorBase):
    id: UUID
    reporte_nomina_id: UUID

    class Config:
        from_attributes: True

# Esquema para la tabla reporte_nomina
class ReporteNominaBase(BaseModel):
    empleado_id: UUID
    fecha_inicio: date
    fecha_fin: date
    total_pagado: Optional[Decimal] = Decimal('0')  # Validación de rango

class ReporteNominaResponse(BaseModel):
    id: UUID
    empleado_id: UUID
    cedula: str
    nombres: str
    apellidos: str
    telefono: str
    puesto_trabajo: str
    fecha_inicio: date
    fecha_fin: date
    descuentos_aplicados: Optional[str]
    subsidios_aplicados: Optional[str]
    recargos_y_valores: Optional[str]
    total_pagado: Decimal

    class Config:
        from_attributes = True

class ReporteNominaCreate(ReporteNominaBase):
    quincena_valores: list[QuincenaValorCreate]
    recargos: list[int]
    descuentos: list[int]
    subsidios: Optional[list[int]] = None
    total_pagado: Optional[Decimal] = Decimal('0')

class ReporteNomina(ReporteNominaBase):
    id: UUID

    class Config:
        from_attributes: True

# Esquema para la tabla reporte_nomina_recargos
class ReporteNominaRecargoBase(BaseModel):
    reporte_nomina_id: UUID
    tipo_recargo_id: int

class ReporteNominaRecargoCreate(ReporteNominaRecargoBase):
    pass

class ReporteNominaRecargo(ReporteNominaRecargoBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla reporte_nomina_descuentos
class ReporteNominaDescuentoBase(BaseModel):
    reporte_nomina_id: UUID
    tipo_descuento_id: int

class ReporteNominaDescuentoCreate(ReporteNominaDescuentoBase):
    pass

class ReporteNominaDescuento(ReporteNominaDescuentoBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla reporte_nomina_subsidios
class ReporteNominaSubsidioBase(BaseModel):
    reporte_nomina_id: UUID
    tipo_subsidio_id: int

class ReporteNominaSubsidioCreate(ReporteNominaSubsidioBase):
    pass

class ReporteNominaSubsidio(ReporteNominaSubsidioBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para el formulario de actulización de nomina
class ReporteNominaUpdateForm(BaseModel):
    empleado_id: UUID
    cedula: str
    nombres: str
    apellidos: str
    fecha_inicio: date
    fecha_fin: date
    quincena_valores: list[QuincenaValorCreate]
    recargos: Optional[list[int]] = None
    descuentos: Optional[list[int]] = None
    subsidios: Optional[list[int]] = None
    total_pagado: Optional[Decimal] = Decimal('0')

    class Config:
        from_attributes = True

# Esquema para actualizar una nómina
class ReporteNominaUpdate(ReporteNominaBase):
    quincena_valores: Optional[list[QuincenaValorCreate]] = None
    recargos: Optional[list[int]] = None
    descuentos: Optional[list[int]] = None
    subsidios: Optional[list[int]] = None
    total_pagado: Optional[Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=False, ge=0)]] = Decimal('0')

    class Config:
        from_attributes = True

# Esquema para eliminar una nómina
class ReporteNominaDelete(BaseModel):
    id: UUID

    class Config:
        from_attributes = True