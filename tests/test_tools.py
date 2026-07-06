import pytest
from app.tools.calcular_itbis import calcular_itbis, ResultadoITBIS
from app.tools.validar_ncf import validar_ncf, ResultadoValidacionNCF
from app.tools.presentar_formato_606 import presentar_formato_606, Resumen606


class TestCalcularITBIS:
    def test_itbis_no_incluido(self):
        r = calcular_itbis(100_000)
        assert r.monto_sin_itbis == 100_000
        assert r.itbis == 18_000
        assert r.monto_con_itbis == 118_000

    def test_itbis_incluido(self):
        r = calcular_itbis(118_000, incluido=True)
        assert r.monto_sin_itbis == 100_000
        assert r.itbis == 18_000
        assert r.monto_con_itbis == 118_000

    def test_monto_cero(self):
        r = calcular_itbis(0)
        assert r.itbis == 0
        assert r.monto_con_itbis == 0

    def test_monto_negativo(self):
        with pytest.raises(ValueError, match="non-negative"):
            calcular_itbis(-100)

    def test_monto_no_numerico(self):
        with pytest.raises(TypeError, match="numeric"):
            calcular_itbis("abc")

    def test_precision_decimal(self):
        r = calcular_itbis(99.99)
        assert r.itbis == 18.0
        assert r.monto_con_itbis == 117.99

    def test_itbis_incluido_precision(self):
        r = calcular_itbis(1000, incluido=True)
        assert r.monto_sin_itbis == 847.46
        assert r.itbis == 152.54
        assert r.monto_con_itbis == 1000


class TestValidarNCF:
    def test_ncf_valido_credito_fiscal(self):
        r = validar_ncf("E010000000001")
        assert r.valido is True
        assert r.tipo_codigo == "01"
        assert r.tipo_nombre == "Factura de Crédito Fiscal"
        assert r.serie == "E"
        assert len(r.errores) == 0

    def test_ncf_valido_consumo(self):
        r = validar_ncf("E020000000001")
        assert r.valido is True
        assert r.tipo_nombre == "Factura de Consumo"

    def test_ncf_serie_b(self):
        r = validar_ncf("B010000000001")
        assert r.valido is True
        assert r.serie == "B"

    def test_ncf_tipo_invalido(self):
        r = validar_ncf("E990000000001")
        assert r.valido is False
        assert any("Tipo NCF inválido" in e for e in r.errores)

    def test_ncf_serie_invalida(self):
        r = validar_ncf("X010000000001")
        assert r.valido is False
        assert any("Serie inválida" in e for e in r.errores)

    def test_ncf_longitud_corta(self):
        r = validar_ncf("E01000")
        assert r.valido is False
        assert any("Longitud" in e for e in r.errores)

    def test_ncf_vacio(self):
        r = validar_ncf("")
        assert r.valido is False

    def test_ncf_no_string(self):
        with pytest.raises(TypeError, match="string"):
            validar_ncf(12345)

    def test_ncf_con_espacios(self):
        r = validar_ncf("  E010000000001  ")
        assert r.valido is True

    def test_ncf_lowercase(self):
        r = validar_ncf("e010000000001")
        assert r.valido is True
        assert r.serie == "E"


class TestPresentarFormato606:
    def test_formato_basico(self):
        r = presentar_formato_606("202606", 42)
        assert r.periodo == "202606"
        assert r.cantidad_registros == 42
        assert r.fecha_limite == "2026-07-15"
        assert r.estado == "pendiente_envio"
        assert "42 registros" in r.mensaje

    def test_formato_sin_movimiento(self):
        r = presentar_formato_606("202601", 0)
        assert r.estado == "sin_movimiento"
        assert "sin movimiento" in r.mensaje

    def test_formato_diciembre(self):
        r = presentar_formato_606("202612", 10)
        assert r.fecha_limite == "2027-01-15"

    def test_periodo_invalido(self):
        with pytest.raises(ValueError, match="YYYYMM"):
            presentar_formato_606("2026-06", 10)

    def test_mes_invalido(self):
        with pytest.raises(ValueError, match="Month"):
            presentar_formato_606("202613", 10)

    def test_registros_negativos(self):
        with pytest.raises(ValueError, match="non-negative"):
            presentar_formato_606("202606", -1)

    def test_periodo_no_string(self):
        with pytest.raises(TypeError, match="string"):
            presentar_formato_606(202606, 10)

    def test_registros_no_int(self):
        with pytest.raises(TypeError, match="integer"):
            presentar_formato_606("202606", 10.5)

    def test_un_registro_singular(self):
        r = presentar_formato_606("202606", 1)
        assert "1 registro de" in r.mensaje
        assert "registros" not in r.mensaje.replace("1 registro de", "")
