from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from pandas import DataFrame


@dataclass
class Member:
    """Classe representando um membro em um sessão."""

    ID: int
    name: str
    balance: float
    weight: float = 1
    description: Optional[str] = None

    def __str__(self):
        return self.name


@dataclass
class Expense:
    """Classe representando um gasto da sessão."""

    ID: int
    name: str
    value: float
    payer: Member
    members: List[Member]
    description: Optional[str] = None

    def __str__(self):
        return f'{self.name}: ${self.value :,.2f}'


class Session:
    """Classe representando uma sessão."""

    def __init__(self, name, description):
        self.ID: int = 0
        self.name: str = name
        self.description: str = description
        self.creation_date: datetime = datetime.now()
        self.tags: List[str] = []
        self.members: DataFrame = DataFrame(
            dict(
                ID=[],
                Name=[],
                Weight=[],
                Balance=[],
                Description=[],
                Ativo=[]
            )
        )

    def add_member(self, member: Member) -> None:
        """Adicionar Membro à Sessão."""

        self.members.loc[len(self.members)] = [
            member.ID,
            member.name,
            member.weight,
            member.balance,
            member.description,
            True
        ]
        self.members.reset_index(drop=True, inplace=True)

    def remove_member(self, ID: int) -> None:
        """Remover Membro da Sessão."""

        if ID in self.members.ID:
            self.members.loc[self.members.ID == ID, 'Ativo'] = False
        else:
            raise ValueError('ID não encontrado. Não foi possível remover o Membro da Sessão.')

    def update_member(self, ID, new_member_info: Member) -> None:
        """Atualizar informações de um Membro existente na Sessão."""

        if ID in self.members.ID:
            self.remove_member(ID)
            self.add_member(new_member_info)
        else:
            raise ValueError('ID não encontrado. Não foi possível remover o Membro da Sessão.')

    def get_members(self, name_filter: List[str] = None, id_filter: List[int] = None,
                    weight_filter: List[float] = None, balance_bigger_than: int = None,
                    balance_smaller_than: int = None) -> DataFrame:
        """Selecionar Membros da Sessão que se encaixam nos filtros aplicados."""

        members_filtered = self.members.copy()
        if name_filter is not None:
            members_filtered = members_filtered[members_filtered.Name.isin(name_filter)]

        elif id_filter is not None:
            members_filtered = members_filtered[members_filtered.ID.isin(id_filter)]

        elif weight_filter is not None:
            members_filtered = members_filtered[members_filtered.Weight.isin(weight_filter)]

        elif balance_bigger_than is not None:
            members_filtered = members_filtered[members_filtered.Balance > balance_bigger_than]

        elif balance_smaller_than is not None:
            members_filtered = members_filtered[members_filtered.Balance < balance_smaller_than]

        return members_filtered

    def add_expense(self):
        """Adicionar Gasto à Sessão."""

        pass

    def remove_expense(self):
        """Remover Gasto da Sessão."""

        pass

    def update_expense(self):
        """Atualizar informações de um Gasto existente na Sessão."""

        pass

    def get_expense(self, name_filter: List[str] = None, id_filter: List[int] = None,
                    value_bigger_than: int = 0, value_smaller_than: int = 1000000,
                    payer_filter: List[Member] = None, participants_filter: List[Member] = None) -> DataFrame:
        """Selecionar Gastos da Sessão que se encaixam nos filtros aplicados."""

        pass

    def update_results(self):
        """Recalcular a distribuição dos Gastos entre os Membros, calculando o Saldo de cada um."""

        pass

    def export_results(self):
        """Exportar os resultados, indicando quem deve pra quem."""

        pass
