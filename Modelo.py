import configparser


class Veiculo(object):
    def __init__(self, dados_veiculo: dict, combustao: bool = False) -> None:
        self.dados = dados_veiculo
        self.combustao = combustao

        self.gastos: dict[str, float] = {}
        self.gasto_total_por_km: float = 0.

        self.config: configparser.ConfigParser

        self.preco_kwh_eletricidade: float = -1.
        self.preco_L_combustivel: float = -1.
        self.preco_troca_oleo: float = -1.

        self._ler_config()

    def processar(self, km_anuais: int = 10000) -> None:
        self.gastos = {
            "Energia": self._gasto_energetico_por_km(),
            "Manutenção": self._gasto_manutencao_por_km(km_anuais=km_anuais),
            "Depreciação": self._gasto_depreciacao_por_km(km_anuais=km_anuais),
            "Seguro": self._gasto_seguro_por_km(km_anuais=km_anuais),
            "Impostos": self._gasto_imposto_por_km(km_anuais=km_anuais),
        }
        for tipo, gasto in self.gastos.items():
            self.gasto_total_por_km += gasto

    def retornar_gasto_total_por_km(self) -> float:
        return self.gasto_total_por_km
    
    def retornar_gastos_detalhados(self) -> dict:
        return self.gastos

    def _ler_config(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(filenames="Configuracoes.ini", encoding="utf-8")
        info_config: dict = {}
        for secao in self.config.sections():
            secao_config = self.config[secao]
            info_config[secao] = {}
            for chave, valor in secao_config.items():
                try:
                    info_config[secao][chave] = eval(valor)
                except:
                    info_config[secao][chave] = valor
        
        self.preco_kwh_eletricidade = info_config["Valores"]["kwh_eletricidade"]
        self.preco_L_combustivel = info_config["Valores"]["l_combustivel"]
        self.preco_troca_oleo = info_config["Valores"]["troca_oleo"]

    def _gasto_energetico_por_km(self) -> float:
        """
        Retorna o gasto energético em BRL/km
        """
        consumo: float = self._pegar_consumo()
        if self.combustao:
            return self.preco_L_combustivel / consumo
        return self.preco_kwh_eletricidade / consumo

    def _pegar_consumo(self) -> float:
        """
        Retorna o gasto energético em km/L para veículo a combustão e km/kWh para EVs
        """
        if self.combustao:
            consumo = float(self.dados["Autonomia (km)"]) / float(self.dados["Capacidade Tanque (L)"])
        else:
            consumo = float(self.dados["Autonomia (km)"]) / float(self.dados["Capacidade Bateria (kWh)"])
        return consumo
    
    def _gasto_manutencao_por_km(self, km_anuais: int) -> float:
        """
        Retorna o gasto com manutenção em BRL/km
        """
        gastos: list[float] = []
        if self.combustao:
            troca_oleo_por_km: float = self._gasto_troca_oleo_por_km(km_anuais=km_anuais)
            gastos.append(troca_oleo_por_km)
        custo_pneus: float = self._gasto_pneu_por_km()
        gastos.append(custo_pneus)
        revisao: float = self.dados["Revisão Média (BRL)"] / km_anuais
        gastos.append(revisao)
        return sum(gastos)
    
    def _gasto_depreciacao_por_km(self, km_anuais: int) -> float:
        """
        Retorna o gasto com a depreciação do veículo por km, em BRL/km
        """
        preco_veiculo = float(self.dados["Valor (BRL)"])
        depreciacao = float(self.dados["Depreciação (%)"]) / 100
        return depreciacao * preco_veiculo / km_anuais
    
    def _gasto_seguro_por_km(self, km_anuais: int) -> float:
        """
        Retorna o gasto com seguro em BRL/km
        """
        seguro: float = self.dados["Seguro"]
        return seguro / km_anuais
    
    def _gasto_imposto_por_km(self, km_anuais: float) -> float:
        """
        Retorna o gasto com IPVA em BRL/km
        """
        valor_ipva = float(self.dados["Valor (BRL)"]) * float(self.dados["IPVA (%)"]) / 100
        return valor_ipva / km_anuais
    
    def _gasto_troca_oleo_por_km(self, km_anuais: int) -> float:
        numero_trocas_anual: int = km_anuais // 5000
        valor_total: float = numero_trocas_anual * self.preco_troca_oleo
        valor_por_km = valor_total / km_anuais
        return valor_por_km

    def _gasto_pneu_por_km(self) -> float:
        custo_kit_pneus = float(self.dados["Pneus (4 un)"])
        km_pneu = float(self.dados["Km Pneu"])
        return custo_kit_pneus / km_pneu
    