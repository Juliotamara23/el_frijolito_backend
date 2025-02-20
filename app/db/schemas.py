from pydantic import BaseModel, condecimal, Field, constr, conint
from typing import Optional, Annotated
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

class EmpleadoDelete(EmpleadoBase):
    pass

class Empleado(EmpleadoBase):
    id: UUID

    class Config:
        from_attributes: True

# Esquema para la tabla config_salario
class ConfigSalarioBase(BaseModel):
    año: str  # Validación de formato de año
    salario_minimo: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=True, ge=0)]  # Validación de rango
    horas_semana: Annotated[int, conint(ge=0, le=168)]  # Validación de rango (máximo 168 horas en una semana)
    horas_mes: Annotated[int, conint(ge=0, le=744)]  # Validación de rango (máximo 744 horas en un mes)
    valor_hora: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=True, ge=0)]  # Validación de rango

class ConfigSalarioCreate(ConfigSalarioBase):
    pass

class ConfigSalario(ConfigSalarioBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla tipo_recargos
class TipoRecargoBase(BaseModel):
    tipo_hora: Annotated[str, constr(min_length=1, max_length=100)]
    porcentaje: Annotated[Decimal, Field(max_digits=5, decimal_places=4, strict=True, ge=0, le=2)]  # Validación de rango (0-1)
    valor_hora: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=True, ge=0)]  # Validación de rango
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
    valor: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=True, ge=0)]  # Validación de rango

class TipoSubsidioCreate(TipoSubsidioBase):
    pass

class TipoSubsidio(TipoSubsidioBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla tipo_descuentos
class TipoDescuentoBase(BaseModel):
    tipo: Annotated[str, constr(min_length=1, max_length=100)]
    valor: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=True, ge=0)]  # Validación de rango

class TipoDescuentoCreate(TipoDescuentoBase):
    pass

class TipoDescuento(TipoDescuentoBase):
    id: int

    class Config:
        from_attributes: True

# Esquema para la tabla reporte_nomina
class ReporteNominaBase(BaseModel):
    empleado_id: UUID
    fecha_inicio: date
    fecha_fin: date
    total_pagado: Annotated[Decimal, Field(max_digits=10, decimal_places=2, strict=True, ge=0)]  # Validación de rango

class ReporteNominaCreate(ReporteNominaBase):
    pass

class ReporteNomina(ReporteNominaBase):
    id: UUID

    class Config:
        from_attributes: True

# Esquema para la tabla quincena_valores
class QuincenaValorBase(BaseModel):
    reporte_nomina_id: UUID
    tipo_recargo_id: int
    cantidad_dias: Annotated[int, conint(ge=0, le=31)]  # Validación de rango (máximo 31 días en un mes)
    valor_quincena: Annotated[Decimal, condecimal(max_digits=10, decimal_places=2), Field(strict=True, ge=0)]  # Validación de rango

class QuincenaValorCreate(QuincenaValorBase):
    pass

class QuincenaValor(QuincenaValorBase):
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