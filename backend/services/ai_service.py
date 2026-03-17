"""AI service with Celery tasks"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.celery_app import celery_app
from backend.models.scan import Scan, ScanAnalysis
from backend.config import settings
from backend.services.scan_service import ScanService


class AIService:
    """AI processing service"""
    
    @staticmethod
    async def analyze_scan(scan_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Orchestrate all AI analyses"""
        scan = await ScanService.get_scan(db, scan_id)
        if not scan:
            raise ValueError("Scan not found")
        
        # Update status
        await ScanService.update_scan_status(db, scan_id, "analyzing")
        
        # Trigger Celery tasks
        visual_task = process_visual_analysis.delay(scan_id, scan.image_url)
        ocr_task = process_ocr_analysis.delay(scan_id, scan.image_url)
        regulatory_task = process_regulatory_check.delay(scan_id, scan.barcode)
        
        return {
            "scan_id": scan_id,
            "status": "analyzing",
            "tasks": {
                "visual": visual_task.id,
                "ocr": ocr_task.id,
                "regulatory": regulatory_task.id,
            }
        }


@celery_app.task(bind=True, name="tasks.process_visual_analysis")
def process_visual_analysis(self, scan_id: str, image_url: str) -> Dict[str, Any]:
    """Visual authenticity analysis"""
    try:
        # Mock: In production, call actual visual AI API
        result = {
            "scan_id": scan_id,
            "visual_features": {
                "label_clarity": 0.95,
                "color_authenticity": 0.92,
                "packaging_integrity": 0.88,
                "brand_consistency": 0.90,
            },
            "authenticity_score": 0.91,
        }
        return result
    except Exception as e:
        self.retry(exc=e, countdown=5, max_retries=3)


@celery_app.task(bind=True, name="tasks.process_ocr_analysis")
def process_ocr_analysis(self, scan_id: str, image_url: str) -> Dict[str, Any]:
    """OCR text extraction and validation"""
    try:
        # Mock: In production, call Tesseract or AWS Textract
        result = {
            "scan_id": scan_id,
            "extracted_text": {
                "product_name": "Product Name",
                "manufacturer": "Manufacturer Ltd",
                "batch_code": "LOT123456",
                "expiry_date": "2026-12-31",
            },
            "text_clarity": 0.87,
        }
        return result
    except Exception as e:
        self.retry(exc=e, countdown=5, max_retries=3)


@celery_app.task(bind=True, name="tasks.process_regulatory_check")
def process_regulatory_check(self, scan_id: str, barcode: str) -> Dict[str, Any]:
    """Check against NAFDAC registry"""
    try:
        # Mock: In production, query NAFDAC database
        result = {
            "scan_id": scan_id,
            "nafdac_status": "approved",
            "is_registered": True,
            "regulatory_score": 0.94,
        }
        return result
    except Exception as e:
        self.retry(exc=e, countdown=5, max_retries=3)


@celery_app.task(bind=True, name="tasks.process_fusion_analysis")
def process_fusion_analysis(self, scan_id: str, visual_result: Dict, ocr_result: Dict, regulatory_result: Dict) -> Dict[str, Any]:
    """Fuse all AI results"""
    try:
        visual_score = visual_result.get("authenticity_score", 0)
        regulatory_score = regulatory_result.get("regulatory_score", 0)
        text_quality = ocr_result.get("text_clarity", 0)
        
        # Weighted fusion
        fusion_score = (visual_score * 0.4) + (regulatory_score * 0.4) + (text_quality * 0.2)
        
        if fusion_score >= 0.85:
            verdict = "authentic"
            risk_level = "low"
        elif fusion_score >= 0.70:
            verdict = "caution"
            risk_level = "medium"
        else:
            verdict = "counterfeit"
            risk_level = "high"
        
        result = {
            "scan_id": scan_id,
            "fusion_score": fusion_score,
            "verdict": verdict,
            "risk_level": risk_level,
            "confidence": fusion_score,
        }
        return result
    except Exception as e:
        self.retry(exc=e, countdown=5, max_retries=3)


@celery_app.task(bind=True, name="tasks.finalize_scan_analysis")
async def finalize_scan_analysis(self, scan_id: str, fusion_result: Dict) -> None:
    """Store final analysis and update scan status"""
    from backend.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Record analysis
            await ScanService.record_analysis(db, scan_id, fusion_result)
            
            # Update status based on verdict
            status = "complete"
            await ScanService.update_scan_status(db, scan_id, status)
            
        except Exception as e:
            self.retry(exc=e, countdown=5, max_retries=3)
