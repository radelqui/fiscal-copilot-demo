import pytest
from app.tools.explicar_componente import explicar_componente, ResultadoComponente
from app.tools.donde_verificar import donde_verificar, ResultadoVerificacion
from app.tools.generar_reporte_arquitectura import generar_reporte_arquitectura, ResultadoReporte


class TestExplicarComponente:
    def test_bedrock_agent(self):
        r = explicar_componente("bedrock_agent")
        assert isinstance(r, ResultadoComponente)
        assert r.componente == "bedrock_agent"
        assert "2BOPZRAI7X" in r.descripcion
        assert r.modelo == "eu.anthropic.claude-sonnet-4-6"

    def test_rag(self):
        r = explicar_componente("rag")
        assert "5I5RDNA2V1" in r.descripcion
        assert "Titan" in r.descripcion

    def test_all_componentes(self):
        for comp in ["bedrock_agent", "rag", "action_groups", "hitl", "guardrails", "evals", "observabilidad", "backend"]:
            r = explicar_componente(comp)
            assert r.componente == comp
            assert r.nombre
            assert r.descripcion

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            explicar_componente("nonexistent")

    def test_normalizes_input(self):
        r = explicar_componente("Bedrock Agent")
        assert r.componente == "bedrock_agent"

    def test_normalizes_dashes(self):
        r = explicar_componente("action-groups")
        assert r.componente == "action_groups"


class TestDondeVerificar:
    def test_bedrock_agent(self):
        r = donde_verificar("bedrock_agent")
        assert isinstance(r, ResultadoVerificacion)
        assert "registry.sypnose.cloud" in r.registry_url
        assert "bedrock_agent.py" in r.registry_path

    def test_all_componentes(self):
        for comp in ["bedrock_agent", "rag", "action_groups", "hitl", "guardrails", "evals", "observabilidad", "backend"]:
            r = donde_verificar(comp)
            assert r.componente == comp
            assert r.registry_url

    def test_unknown_raises(self):
        with pytest.raises(ValueError):
            donde_verificar("invalid")


class TestGenerarReporteArquitectura:
    def test_todas(self):
        r = generar_reporte_arquitectura("todas")
        assert isinstance(r, ResultadoReporte)
        assert r.estado == "PENDIENTE_APROBACION"
        assert len(r.secciones) == 8

    def test_specific_sections(self):
        r = generar_reporte_arquitectura("rag,hitl")
        assert r.secciones == ["rag", "hitl"]
        assert r.estado == "PENDIENTE_APROBACION"

    def test_invalid_section(self):
        with pytest.raises(ValueError):
            generar_reporte_arquitectura("invalid_section")

    def test_empty_means_all(self):
        r = generar_reporte_arquitectura("")
        assert len(r.secciones) == 8
