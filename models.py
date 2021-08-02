from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from pandas import DataFrame

# TODO: Testar modelagem simples (IMPORTANT)

# TODO: Criar features pra modelagem mais complexa
#  > Conta da sessão, com:
#   - Investimento inicial
#   - Aportes
#  > Novos tipos de Gastos:
#   - Gastos constantes, e gastos pontuais
#  > Informações de pagamento dos membros da sessão
#  > Finalizar sessão pra algum membro. Ajustar as contas dele com os outros, e seguir com a Sessão.


@dataclass
class Member:
    """Classe representando um membro em um sessão."""

    ID: int
    name: str
    paid: float = 0
    balance: float = 0
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
                Paid=[],
                Description=[],
                Ativo=[]
            )
        )
        self.expenses: DataFrame = DataFrame(
            dict(
                ID=[],
                name=[],
                value=[],
                payer=[],
                members=[],
                description=[]
            )
        )

    def add_member(self, member: Member) -> None:
        """Adicionar Membro à Sessão."""

        self.members.loc[len(self.members)] = [
            member.ID,
            member.name,
            member.weight,
            member.balance,
            member.paid,
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

    def update_member(self, ID: int, new_member_info: Member) -> None:
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

    def add_expense(self, expense: Expense) -> None:
        """Adicionar Gasto à Sessão."""

        self.expenses.loc[len(self.expenses)] = [
            expense.ID,
            expense.name,
            expense.value,
            expense.payer.ID,
            [member.ID for member in expense.members],
            expense.description
        ]
        self.expenses.reset_index(drop=True, inplace=True)

    def remove_expense(self, ID: int) -> None:
        """Remover Gasto da Sessão."""

        if ID in self.expenses.ID:
            self.expenses.loc[self.expenses.ID == ID, 'Ativo'] = False
        else:
            raise ValueError('ID não encontrado. Não foi possível remover o Gasto da Sessão.')

    def update_expense(self, ID: int, new_expense_info: Expense) -> None:
        """Atualizar informações de um Gasto existente na Sessão."""

        self.remove_expense(ID)
        self.add_expense(new_expense_info)

    def get_expense(self, name_filter: List[str] = None, id_filter: List[int] = None,
                    value_bigger_than: int = None, value_smaller_than: int = None,
                    payer_filter: List[int] = None, participants_filter: List[int] = None) -> DataFrame:
        """Selecionar Gastos da Sessão que se encaixam nos filtros aplicados."""

        expenses_filtered = self.expenses.copy()
        if name_filter is not None:
            expenses_filtered = expenses_filtered[expenses_filtered.Name.isin(name_filter)]

        elif id_filter is not None:
            expenses_filtered = expenses_filtered[expenses_filtered.ID.isin(id_filter)]

        elif value_bigger_than is not None:
            expenses_filtered = expenses_filtered[expenses_filtered.Value > value_bigger_than]

        elif value_smaller_than is not None:
            expenses_filtered = expenses_filtered[expenses_filtered.Name < value_smaller_than]

        elif payer_filter is not None:
            expenses_filtered = expenses_filtered[expenses_filtered.Payer.isin(payer_filter)]

        elif participants_filter is not None:
            expenses_filtered = expenses_filtered[expenses_filtered.Participants.isin(participants_filter)]

        return expenses_filtered

    def update_results(self):
        """Recalcular a distribuição dos Gastos entre os Membros, calculando o Saldo de cada um."""

        for expense in self.expenses[self.expenses.Ativo].itertuples():
            payer = expense.Payer
            members = expense.Members
            weights = [float(self.get_members(id_filter=[member]).at[0, 'Weight']) for member in members]

            total_value = 0
            for weight in weights:
                total_value += expense.Value * weight

            total_value /= sum(weights)
            for member, weight in zip(members, weights):
                balance_to_add = total_value * weight
                self.get_members(id_filter=[member]).at[0, 'Balance'] += balance_to_add
            self.get_members(id_filter=payer).at[0, 'Paid'] += expense.Value

    def export_results(self):
        """Exportar os resultados, indicando quem deve pra quem."""

        non_zero_members = self.members[self.members.Balance != 0].unique().tolist()
        active_members = self.members[self.members.Ativo].unique().tolist()

        movimentacoes = dict()
        while len(non_zero_members) > 0:
            non_zero_members_set = set(non_zero_members)
            active_members_set = set(active_members)
            members_to_loop = list(non_zero_members_set.intersection(active_members_set))

            for index, member_id in enumerate(members_to_loop):
                curr_member = self.get_members(id_filter=[member_id]).loc[0]
                last_member = self.get_members(id_filter=[members_to_loop[index - 1]]).loc[0]

                if curr_member.Balance < 0:
                    negative_balance = curr_member.Balance
                    positive_balance = last_member.Balance

                    # Transferir o valor do maior saldo absoluto. Se negativo for maior, transferir ele, e vice-versa
                    balance_to_transfer = max([abs(negative_balance), abs(positive_balance)])
                    curr_member.Balance += balance_to_transfer
                    last_member.Balance -= balance_to_transfer

                    movimentacao_key = f'{member_id}p{members_to_loop[index - 1]}'
                    if movimentacao_key in movimentacoes.keys():
                        movimentacoes[movimentacao_key] += balance_to_transfer
                    else:
                        movimentacoes[movimentacao_key] = balance_to_transfer
                    break
        return movimentacoes

    def _get_min_expense(self):
        """Selecionar o menor dos Gastos da viagem."""
        pass

    def _get_max_expense(self):
        """Selecionar o maior dos Gastos da viagem."""
        pass

    def create_expenses_report(self):
        """Gerar relatório de todas os Gastos."""
        pass

if __name__ == '__main__':
    viagem_praia = Session(name='Viagem à Praia', description='Viagem Guarulhos -> Praia Grande com os mlk')

    lucas = Member(ID=0, name='Lucas', description='Lucas Petersen')
    jaci = Member(ID=1, name='Jaci', description='Gustavo Livino')
    wag = Member(ID=2, name='Wag', description='Wilgner Macena')

    viagem_praia.add_member(lucas)
    viagem_praia.add_member(jaci)
    viagem_praia.add_member(wag)

    gasolina = Expense(ID=0, members=[jaci, lucas, wag], payer=lucas, name='Posto de Gasolina', value=120)
    carro = Expense(ID=1, members=[jaci, wag, lucas], payer=wag, name='Aluguel do Carro', value=450)
    mercado = Expense(ID=2, members=[jaci, wag, lucas], payer=lucas, name='Supermercado', value=230)
    lanches = Expense(ID=3, members=[jaci, wag, lucas], payer=jaci, name='Lanches da Hamburgueria', value=65)

    viagem_praia.add_expense(gasolina)
    viagem_praia.add_expense(carro)
    viagem_praia.add_expense(mercado)
    viagem_praia.add_expense(lanches)

    viagem_praia.update_results()
    movs = viagem_praia.export_results()
    print(movs)
