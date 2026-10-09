"""esquema inicial

Revision ID: 0001_esquema_inicial
Revises:
Create Date: 2026-10-09 15:38:12.920964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001_esquema_inicial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Equivale al esquema que antes creaba Base.metadata.create_all al arrancar
    op.create_table('doctores',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nombres', sa.String(length=100), nullable=True),
    sa.Column('apellidos', sa.String(length=100), nullable=True),
    sa.Column('correo', sa.String(length=100), nullable=False),
    sa.Column('especialidad', sa.String(length=100), nullable=True),
    sa.Column('cedula', sa.String(length=50), nullable=True),
    sa.Column('telefono', sa.String(length=50), nullable=True),
    sa.Column('password_hash', sa.Text(), nullable=True),
    sa.Column('embedding_facial', sa.Text(), nullable=True),
    sa.Column('rol', sa.String(length=20), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('doctores', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_doctores_correo'), ['correo'], unique=True)
        batch_op.create_index(batch_op.f('ix_doctores_id'), ['id'], unique=False)

    op.create_table('pacientes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('dni', sa.String(length=20), nullable=False),
    sa.Column('nombres', sa.String(length=100), nullable=False),
    sa.Column('apellidos', sa.String(length=100), nullable=False),
    sa.Column('telefono', sa.String(length=20), nullable=True),
    sa.Column('correo', sa.String(length=100), nullable=True),
    sa.Column('fecha_nacimiento', sa.String(length=50), nullable=True),
    sa.Column('direccion', sa.Text(), nullable=True),
    sa.Column('genero', sa.String(length=10), nullable=True),
    sa.Column('password_hash', sa.Text(), nullable=True),
    sa.Column('embedding_facial', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('pacientes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_pacientes_dni'), ['dni'], unique=True)
        batch_op.create_index(batch_op.f('ix_pacientes_id'), ['id'], unique=False)

    op.create_table('citas',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('paciente_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.String(length=50), nullable=True),
    sa.Column('hora', sa.String(length=20), nullable=True),
    sa.Column('estado', sa.String(length=30), nullable=True),
    sa.Column('motivo', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctores.id'], ),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('citas', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_citas_id'), ['id'], unique=False)

    op.create_table('expedientes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('paciente_id', sa.Integer(), nullable=False),
    sa.Column('alergias_conocidas', sa.Text(), nullable=True),
    sa.Column('padecimientos_cronicos', sa.Text(), nullable=True),
    sa.Column('grupo_sanguineo', sa.String(length=5), nullable=True),
    sa.Column('factor_rh', sa.String(length=2), nullable=True),
    sa.Column('historial_resumido', sa.Text(), nullable=True),
    sa.Column('antecedentes_familiares', sa.Text(), nullable=True),
    sa.Column('antecedentes_quirurgicos', sa.Text(), nullable=True),
    sa.Column('habitos_salud', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('expedientes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_expedientes_id'), ['id'], unique=False)

    op.create_table('consultas',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('expediente_id', sa.Integer(), nullable=False),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('cita_id', sa.Integer(), nullable=True),
    sa.Column('fecha_consulta', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('motivo_consulta', sa.Text(), nullable=True),
    sa.Column('sintomas', sa.Text(), nullable=True),
    sa.Column('signos_vitales', sa.Text(), nullable=True),
    sa.Column('diagnostico_principal', sa.Text(), nullable=True),
    sa.Column('diagnostico_diferencial', sa.Text(), nullable=True),
    sa.Column('notas_doctor', sa.Text(), nullable=True),
    sa.Column('tipo_consulta', sa.String(length=30), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['cita_id'], ['citas.id'], ),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctores.id'], ),
    sa.ForeignKeyConstraint(['expediente_id'], ['expedientes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('consultas', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_consultas_id'), ['id'], unique=False)

    op.create_table('llamadas',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('cita_id', sa.Integer(), nullable=False),
    sa.Column('paciente_id', sa.Integer(), nullable=True),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('room_id', sa.String(length=50), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('duracion', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['cita_id'], ['citas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctores.id'], ),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('room_id')
    )
    with op.batch_alter_table('llamadas', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_llamadas_id'), ['id'], unique=False)

    op.create_table('examenes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('consulta_id', sa.Integer(), nullable=False),
    sa.Column('paciente_id', sa.Integer(), nullable=True),
    sa.Column('doctor_solicitante_id', sa.Integer(), nullable=True),
    sa.Column('tipo_examen', sa.String(length=50), nullable=True),
    sa.Column('nombre_examen', sa.String(length=150), nullable=False),
    sa.Column('categoria', sa.String(length=50), nullable=True),
    sa.Column('resultado', sa.Text(), nullable=True),
    sa.Column('archivo_url', sa.String(length=255), nullable=True),
    sa.Column('es_imagen', sa.Boolean(), nullable=True),
    sa.Column('fecha_solicitud', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('fecha_resultado', sa.DateTime(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=True),
    sa.Column('notas_doctor', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['consulta_id'], ['consultas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['doctor_solicitante_id'], ['doctores.id'], ),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('examenes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_examenes_id'), ['id'], unique=False)

    op.create_table('recetas',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('consulta_id', sa.Integer(), nullable=False),
    sa.Column('paciente_id', sa.Integer(), nullable=True),
    sa.Column('doctor_id', sa.Integer(), nullable=True),
    sa.Column('nombre_medicamento', sa.String(length=150), nullable=False),
    sa.Column('concentracion', sa.String(length=50), nullable=True),
    sa.Column('presentacion', sa.String(length=50), nullable=True),
    sa.Column('dosis', sa.String(length=100), nullable=True),
    sa.Column('frecuencia', sa.String(length=100), nullable=True),
    sa.Column('duracion_tratamiento', sa.String(length=50), nullable=True),
    sa.Column('indicaciones_especiales', sa.Text(), nullable=True),
    sa.Column('fecha_receta', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
    sa.ForeignKeyConstraint(['consulta_id'], ['consultas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['doctor_id'], ['doctores.id'], ),
    sa.ForeignKeyConstraint(['paciente_id'], ['pacientes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_recetas_id'), ['id'], unique=False)



def downgrade() -> None:
    # Equivale al esquema que antes creaba Base.metadata.create_all al arrancar
    with op.batch_alter_table('recetas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_recetas_id'))

    op.drop_table('recetas')
    with op.batch_alter_table('examenes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_examenes_id'))

    op.drop_table('examenes')
    with op.batch_alter_table('llamadas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_llamadas_id'))

    op.drop_table('llamadas')
    with op.batch_alter_table('consultas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_consultas_id'))

    op.drop_table('consultas')
    with op.batch_alter_table('expedientes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_expedientes_id'))

    op.drop_table('expedientes')
    with op.batch_alter_table('citas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_citas_id'))

    op.drop_table('citas')
    with op.batch_alter_table('pacientes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_pacientes_id'))
        batch_op.drop_index(batch_op.f('ix_pacientes_dni'))

    op.drop_table('pacientes')
    with op.batch_alter_table('doctores', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_doctores_id'))
        batch_op.drop_index(batch_op.f('ix_doctores_correo'))

    op.drop_table('doctores')
