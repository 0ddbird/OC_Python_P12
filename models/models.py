from datetime import datetime
from decimal import Decimal
from typing import Optional

from passlib.context import CryptContext
from sqlmodel import Column, Field, ForeignKey, Integer, Relationship, SQLModel, Table

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

sales_permission_table = Table(
    "sales_permission",
    SQLModel.metadata,
    Column("sales_rep_id", Integer, ForeignKey("sales_rep.id")),
    Column("permission_id", Integer, ForeignKey("permission.id")),
)

support_permission_table = Table(
    "support_permission",
    SQLModel.metadata,
    Column("support_rep_id", Integer, ForeignKey("support_rep.id")),
    Column("permission_id", Integer, ForeignKey("permission.id")),
)

manager_permission_table = Table(
    "manager_permission",
    SQLModel.metadata,
    Column("manager_id", Integer, ForeignKey("manager.id")),
    Column("permission_id", Integer, ForeignKey("permission.id")),
)


class Permission(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    description: str


class Collaborator(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    _password_hash: str = Field(alias="password")

    @property
    def password(self):
        raise AttributeError("Access to password is forbidden")

    @password.setter
    def password(self, plain_password):
        self._password_hash = pwd_context.hash(plain_password)

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self._password_hash)


class SalesRep(Collaborator, table=True):
    contracts: list["Contract"] = Relationship(back_populates="sales_rep")
    permissions: list[Permission] = Relationship(link_model=sales_permission_table)


class SupportRep(Collaborator, table=True):
    events: list["Event"] = Relationship(back_populates="support_rep")
    permissions: list[Permission] = Relationship(link_model=support_permission_table)


class Manager(Collaborator, table=True):
    permissions: list[Permission] = Relationship(link_model=manager_permission_table)


class Company(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    customers: list["Customer"] = Relationship(back_populates="company")


class Customer(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str
    informations: str
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    company: Company = Relationship(back_populates="customers")
    sales_rep_id: Optional[int] = Field(default=None, foreign_key="sales_rep.id")
    sales_rep: SalesRep = Relationship(back_populates="customers")
    contracts_id: list[int] = Field(default=None, foreign_key="contracts.id")
    contracts: "Contract" = Relationship(back_populates="customer")
    created_on: datetime = Field(default_factory=datetime.now)
    updated_on: datetime = Field(default_factory=datetime.now, onupdate=datetime.now)


class ContractStatus(str, SQLModel):
    DRAFT: str = "draft"
    SIGNED: str = "signed"
    CANCELED: str = "canceled"


class Contract(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    status: ContractStatus = Field(default=ContractStatus.DRAFT.value)
    customer: Customer = Relationship(back_populates="contracts")
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")
    sales_rep: SalesRep = Relationship(back_populates="contracts")
    sales_rep_id: Optional[int] = Field(default=None, foreign_key="sales_rep.id")
    event: "Event" = Relationship(back_populates="contract")
    event_id: Optional[int] = Field(default=None, foreign_key="event.id")
    total_value: Decimal = Field(max_digits=9, decimal_places=2)
    remaining_balance: Decimal = Field(max_digits=9, decimal_places=2)
    created_on: datetime = Field(default_factory=datetime.now)
    updated_on: datetime = Field(default_factory=datetime.now, onupdate=datetime.now)


class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    start_date: datetime
    end_date: datetime
    location: str
    attendees: int
    notes: str
    contract: Contract = Relationship(back_populates="event")
    contract_id: Optional[int] = Field(default=None, foreign_key="contract.id")
    support_rep: Optional[SupportRep] = Relationship(
        default=None, back_populates="events"
    )
    support_rep_id: Optional[int] = Field(default=None, foreign_key="support_rep.id")
    created_on: datetime = Field(default_factory=datetime.now)
    updated_on: datetime = Field(default_factory=datetime.now, onupdate=datetime.now)
