from flask_login import UserMixin
from sqlalchemy import Column, DateTime, Integer, String, Boolean
from werkzeug.security import check_password_hash, generate_password_hash
import re
from src.database import Base


class UserDelivery(UserMixin, Base):
    """User account model."""

    __tablename__ = "flasklogin_delivery_users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    cpf = Column(String(11), unique=True, nullable=True)
    password = Column(String(200), nullable=False)
    created_on = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default=True)
    alterar_senha = Column(Boolean, default=True, nullable=False)

    def set_password(self, password):
        """Create hashed password."""
        if not self.is_valid_password(password):
            raise ValueError(
                "A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, números e símbolos."
            )
        self.password = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def is_valid_cpf(self):
        """Validate CPF format and checksum."""
        cpf = self.cpf
        if not re.fullmatch(r"\d{11}", cpf):
            return False

        # Cálculo dos dígitos verificadores
        def calc_digit(cpf, weights):
            s = sum(int(cpf[i]) * weights[i] for i in range(len(weights)))
            d = (s * 10) % 11
            return 0 if d == 10 else d

        first_weights = range(10, 1, -1)
        second_weights = range(11, 2, -1)
        return calc_digit(cpf, first_weights) == int(cpf[9]) and calc_digit(
            cpf, second_weights
        ) == int(cpf[10])

    def is_valid_password(self, password):
        """Validate password strength."""
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    def toggle_active(self):
        """Toggle the active status of the user."""
        self.is_active = not self.is_active

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.name,
            "cpf": self.cpf,
            "role": self.role,
            "created_on": self.created_on,
            "last_login": self.last_login,
        }

    def __repr__(self):
        return f"<User {self.name}>"
