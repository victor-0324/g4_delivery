from sqlalchemy import Column, Integer, String, DateTime, func
from src.database import Base


class Bairros(Base):
    """Bairros"""

    __tablename__ = "bairros"
    id = Column(Integer, primary_key=True)
    nome = Column(String(120))
    tipo = Column(String(100))
    valor_dia = Column(String(20))
    valor_noite = Column(String(20))
    poligono = Column(String(150))
    criado_em = Column(DateTime, server_default=func.now())

    @classmethod
    def from_json(cls, data_json):
        return cls(
            nome=data_json.get("nome"),
            tipo=data_json.get("tipo"),
            valor_dia=data_json.get("valor_dia"),
            valor_noite=data_json.get("valor_noite"),
            poligono=data_json.get("poligono")
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo,
            "valor_dia": self.valor_dia,
            "valor_noite": self.valor_noite,
            "poligono": self.poligono,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
        }

