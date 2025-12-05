from sqlalchemy import Column, Integer, ForeignKey, DateTime, func, UniqueConstraint
from app.database import Base

class LembrancinhaDB(Base):
    __tablename__ = "lembrancinhas"

    id = Column(Integer, primary_key=True, index=True)
    # Atenção aos nomes: você está usando id_cliente em Pedido e Carrinho
    id_cliente = Column(Integer, ForeignKey("usuarios.id_cliente"), nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("id_cliente", name="uq_lembrancinha_cliente"),
    )
