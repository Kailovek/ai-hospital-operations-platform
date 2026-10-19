def test_health_reports_demo_dependencies_truthfully(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "service": "ai-hospital-operations-platform",
        "status": "healthy",
        "mode": "demo",
        "dependencies": {
            "database": "ready",
            "cache": "disabled",
            "vector_store": "local",
            "llm": "ready",
            "model_service": "disabled",
        },
    }
