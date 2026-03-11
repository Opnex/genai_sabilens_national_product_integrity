from app.ocr_linguistic.pipeline import run_pipeline

def test_pipeline_runs():

    result = run_pipeline("tests/sample_images/vaseline.jpg")

    assert "final_text_anomaly_score" in result