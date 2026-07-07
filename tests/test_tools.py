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

    def test_desarrollo_agentico(self):
        r = explicar_componente("desarrollo_agentico")
        assert r.nombre == "Desarrollo Agéntico"
        assert "AGENTS.md" in r.archivo_clave

    def test_multi_model(self):
        r = explicar_componente("multi_model")
        assert r.nombre == "Comparativa Multi-Modelo"
        assert "router.py" in r.archivo_clave


class TestDetectarRequisito:
    def test_action_flows_maps_to_bedrock(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("agentes sobre AWS Bedrock con action flows, permisos, estados y trazabilidad")
        assert r is not None
        assert "bedrock_agent" in r.componentes
        assert "Bedrock Agent" in r.confirma

    def test_rag_multifuente(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("RAG retrieval-aware sobre múltiples fuentes, source attribution")
        assert r is not None
        assert "rag" in r.componentes

    def test_eval_harness(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("eval harnesses para medir factualidad, completitud, coste y latencia")
        assert r is not None
        assert "evals" in r.componentes

    def test_hitl(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("human-in-the-loop: revisión, aprobación, rechazo y escalado")
        assert r is not None
        assert "hitl" in r.componentes

    def test_guardrails(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("guardrails, límites y controles contra prompt injection")
        assert r is not None
        assert "guardrails" in r.componentes

    def test_desarrollo_agentico_req(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("desarrollo agéntico: specs, coding agents, Skills y evals")
        assert r is not None
        assert "desarrollo_agentico" in r.componentes

    def test_tradeoffs(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("trade-offs entre modelos (coste, latencia, calidad)")
        assert r is not None
        assert "multi_model" in r.componentes

    def test_no_match_returns_none(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("¿Cuánto cuesta un helado?")
        assert r is None

    def test_backend_python(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("backend Python/FastAPI, manejo de errores, APIs de LLM y PostgreSQL")
        assert r is not None
        assert "backend" in r.componentes

    def test_workflows_structured(self):
        from app.tools.explicar_componente import detectar_requisito
        r = detectar_requisito("workflows structured outputs y tool calling")
        assert r is not None
        assert "action_groups" in r.componentes


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
