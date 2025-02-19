from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

# Modelo de empleados
class Empleado(Base):
    __tablename__ = 'empleados'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cedula = Column(String, unique=True, nullable=False)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    telefono = Column(String)
    puesto_trabajo = Column(String)
    salario_base = Column(Numeric(10, 2), nullable=False)

    reporte_nominas = relationship("ReporteNomina", back_populates="empleado")

# Modelo de configuración de salario
class ConfigSalario(Base):
    __tablename__ = 'config_salario'

    id = Column(Integer, primary_key=True, index=True)
    año = Column(String, unique=True, nullable=False)
    salario_minimo = Column(Numeric(10, 2), nullable=False)
    horas_semana = Column(Integer, nullable=False)
    horas_mes = Column(Integer, nullable=False)
    valor_hora = Column(Numeric(10, 2), nullable=False)

    reporte_nomina = relationship("ReporteNomina", back_populates="config_salario")

# Modelo de tipo de recargos
class TipoRecargo(Base):
    __tablename__ = 'tipo_recargos'

    id = Column(Integer, primary_key=True, index=True)
    tipo_hora = Column(String, unique=True, nullable=False)
    porcentaje = Column(Numeric(10, 2), nullable=False)
    valor_hora = Column(Numeric(10, 2), nullable=False)
    detalle = Column(String)

    quincena_valores = relationship("QuincenaValor", back_populates="tipo_recargo")
    reporte_nomina_recargos = relationship("ReporteNominaRecargo", back_populates="tipo_recargo")

# Modelo de subsidios
class TipoSubsidio(Base):
    __tablename__ = 'tipo_subsidios'

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, unique=True, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)

    reporte_nomina_subsidios = relationship("ReporteNominaSubsidio", back_populates="tipo_subsidio")

# Modelo de descuentos
class TipoDescuento(Base):
    __tablename__ = 'tipo_descuentos'

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, unique=True, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)

    reporte_nomina_descuentos = relationship("ReporteNominaDescuento", back_populates="tipo_descuento")

# Modelo de Nomina
class ReporteNomina(Base):
    __tablename__ = 'reporte_nominas'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    empleado_id = Column(UUID(as_uuid=True), ForeignKey('empleados.id'), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    total_pagado = Column(Numeric(10, 2), nullable=False)

    empleado = relationship("Empleado", back_populates="reporte_nominas")
    config_salario = relationship("ConfigSalario", back_populates="reporte_nomina")
    quincena_valores = relationship("QuincenaValor", back_populates="reporte_nomina")
    reporte_nomina_recargos = relationship("ReporteNominaRecargo", back_populates="reporte_nomina")
    reporte_nomina_descuentos = relationship("ReporteNominaDescuento", back_populates="reporte_nomina")
    reporte_nomina_subsidios = relationship("ReporteNominaSubsidio", back_populates="reporte_nomina")

# Modelo de quincena valores
class QuincenaValor(Base):
    __tablename__ = 'quincena_valores'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    reporte_nomina_id = Column(UUID(as_uuid=True), ForeignKey('reporte_nominas.id'), nullable=False)
    tipo_recargo_id = Column(Integer, ForeignKey('tipo_recargos.id'), nullable=False)
    cantidad_dias = Column(Integer, nullable=False)
    valor_quincena = Column(Numeric(10, 2), nullable=False)

    reporte_nomina = relationship("ReporteNomina", back_populates="quincena_valores")
    tipo_recargo = relationship("TipoRecargo", back_populates="quincena_valores")

# Modelo de reporte nomina recargos
class ReporteNominaRecargo(Base):
    __tablename__ = 'reporte_nomina_recargos'

    id = Column(Integer, primary_key=True, index=True)
    reporte_nomina_id = Column(UUID(as_uuid=True), ForeignKey('reporte_nominas.id'), nullable=False)
    tipo_recargo_id = Column(Integer, ForeignKey('tipo_recargos.id'), nullable=False)
    
    reporte_nomina = relationship("ReporteNomina", back_populates="reporte_nomina_recargos")
    tipo_recargo = relationship("TipoRecargo", back_populates="reporte_nomina_recargos")

# Modelo de reporte nomina descuentos
class ReporteNominaDescuento(Base):
    __tablename__ = 'reporte_nomina_descuentos'

    id = Column(Integer , primary_key=True, index=True)
    reporte_nomina_id = Column(UUID(as_uuid=True), ForeignKey('reporte_nominas.id'), nullable=False)
    tipo_descuento_id = Column(Integer, ForeignKey('tipo_descuentos.id'), nullable=False)

    reporte_nomina = relationship("ReporteNomina", back_populates="reporte_nomina_descuentos")
    tipo_descuento = relationship("TipoDescuento", back_populates="reporte_nomina_descuentos")

# Modelo de reporte nomina subsidios
class ReporteNominaSubsidio(Base):
    __tablename__ = 'reporte_nomina_subsidios'

    id = Column(Integer, primary_key=True, index=True)
    reporte_nomina_id = Column(UUID(as_uuid=True), ForeignKey('reporte_nominas.id'), nullable=False)
    tipo_subsidio_id = Column(Integer, ForeignKey('tipo_subsidios.id'), nullable=False)

    reporte_nomina = relationship("ReporteNomina", back_populates="reporte_nomina_subsidios")
    tipo_subsidio = relationship("TipoSubsidio", back_populates="reporte_nomina_subsidios")