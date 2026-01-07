from src.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    JSON,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship


class G4DeliveryEmpresas(Base):
    __tablename__ = "g4_delivery_empresas"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False, unique=True)
    credito = Column(Numeric(10, 2), nullable=False, default=0)
    endereco = Column(String(100), nullable=False)
    lat = Column(String(100), default="0")
    lon = Column(String(100), default="0")
    status = Column(String(20), default="ativo")

    pedidos = relationship("G4DeliveryContabilizar", back_populates="empresa")

    @classmethod
    def from_json(cls, data_json):
        return cls(
            nome=data_json.get("nome"),
            telefone=data_json.get("telefone"),
            credito=float(data_json.get("credito", 0)),
            endereco=data_json.get("endereco"),
            lat=data_json.get("lat", "0"),
            lon=data_json.get("lon", "0"),
            status=data_json.get("status", "ativo"),
        )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "credito": float(self.credito),
            "endereco": self.endereco,
            "lat": self.lat,
            "lon": self.lon,
            "status": self.status,
        }


class G4DeliveryMotoboy(Base):
    __tablename__ = "g4_delivery_motoboys"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    status = Column(String(50), default="off")
    cpf = Column(String(14), nullable=False, unique=True)
    placa = Column(String(10), nullable=False)
    lat = Column(String(150), default="0")
    lon = Column(String(150), default="0")
    inicio_entrega = Column(DateTime, default=None)
    duracao_entrega = Column(String(100), default="")
    destino = Column(String(100), default="")
    hora_livre = Column(DateTime, default=None)
    id_pedido = Column(String(50), nullable=True, default=None)
    etiqueta = Column(JSON, nullable=True)
    pix = Column(String(200), nullable=True)

    fretes = relationship("G4DeliveryContabilizar", back_populates="motoboy")

    @classmethod
    def from_json(cls, data_json):
        return cls(
            nome=data_json.get("nome"),
            telefone=data_json.get("telefone"),
            cpf=data_json.get("cpf"),
            placa=data_json.get("placa"),
            lat=data_json.get("lat", "0"),
            lon=data_json.get("lon", "0"),
            status=data_json.get("status"),
            etiqueta=data_json.get("etiqueta", None),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "cpf": self.cpf,
            "placa": self.placa,
            "lat": self.lat,
            "lon": self.lon,
            "inicio_entrega": (
                self.inicio_entrega.isoformat() if self.inicio_entrega else None
            ),
            "duracao_entrega": self.duracao_entrega,
            "destino": self.destino,
            "hora_livre": self.hora_livre.isoformat() if self.hora_livre else None,
            "id_pedido": self.id_pedido,
            "etiqueta": self.etiqueta,
            "status": self.status,
            "pix": self.pix,
        }


class G4DeliveryClientes(Base):
    __tablename__ = "g4_delivery_clientes"

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)

    @classmethod
    def from_json(cls, data_json):
        return cls(
            nome=data_json.get("nome"),
            telefone=data_json.get("telefone"),
            status=data_json.get("status"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "status": self.status,
        }


class G4DeliveryContabilizar(Base):
    __tablename__ = "g4_delivery_contabilizar"

    id = Column(Integer, primary_key=True)

    valor = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False)

    empresa_id = Column(Integer, ForeignKey("g4_delivery_empresas.id"), nullable=True)

    telefone = Column(String(20), nullable=True)
    id_mensagem = Column(String(100))

    retirada_lat = Column(String(100), nullable=True)
    retirada_lon = Column(String(100), nullable=True)
    entrega_lat = Column(String(100), nullable=True)
    entrega_lon = Column(String(100), nullable=True)
    endereco_entrega = Column(String(200))
    via = Column(String(20), nullable=False)
    recusou = Column(JSON)
    hora_pedido = Column(DateTime, default=None)
    hora_aceite = Column(DateTime, default=None)
    hora_espera = Column(DateTime, default=None)

    motoboy_id = Column(Integer, ForeignKey("g4_delivery_motoboys.id"), nullable=True)

    empresa = relationship("G4DeliveryEmpresas", back_populates="pedidos")
    motoboy = relationship("G4DeliveryMotoboy", back_populates="fretes")

    @classmethod
    def from_json(cls, data_json):
        return cls(
            valor=data_json.get("valor"),
            telefone=data_json.get("telefone"),
            status=data_json.get("status"),
            id_mensagem=data_json.get("id_mensagem"),
            retirada_lat=data_json.get("retirada_lat"),
            retirada_lon=data_json.get("retirada_lon"),
            entrega_lat=data_json.get("entrega_lat"),
            entrega_lon=data_json.get("entrega_lon"),
            endereco_entrega=data_json.get("endereco_entrega"),
            via=data_json.get("via"),
            motoboy_id=data_json.get("motoboy_id"),
            recusou=data_json.get("recusou"),
            hora_pedido=data_json.get("hora_pedido"),
            hora_aceite=data_json.get("hora_aceite"),
            hora_espera=data_json.get("hora_espera"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "valor": self.valor,
            "telefone": self.telefone,
            "status": self.status,
            "id_mensagem": self.id_mensagem,
            "retirada_lat": self.retirada_lat,
            "retirada_lon": self.retirada_lon,
            "entrega_lat": self.entrega_lat,
            "entrega_lon": self.entrega_lon,
            "endereco_entrega": self.endereco_entrega,
            "via": self.via,
            "motoboy_id": self.motoboy_id,
            "recusou": self.recusou,
            "hora_pedido": self.hora_pedido,
            "hora_aceite": self.hora_aceite,
            "hora_espera": self.hora_espera,
        }
