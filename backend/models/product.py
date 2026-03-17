"""Product models"""
from datetime import datetime, date
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, TEXT, Date, Index, Enum as SQLEnum, Numeric, Boolean, LargeBinary
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    DISCONTINUED = "discontinued"


class BarcodeType(str, enum.Enum):
    UPC = "UPC"
    EAN = "EAN"
    QR = "QR"
    CODE128 = "CODE128"
    OTHER = "OTHER"


class EmbeddingType(str, enum.Enum):
    VISUAL = "visual"
    OCR = "ocr"
    REGULATORY = "regulatory"
    FUSION = "fusion"
    MULTI_MODAL = "multi_modal"


class ProductCategory(Base):
    """Product categories table"""
    __tablename__ = "product_categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(TEXT)
    parent_id = Column(String(36))  # Self-referencing FK
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class Product(Base):
    """Products table"""
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    company_id = Column(String(36), nullable=False)  # FK to companies
    name = Column(String(255), nullable=False)
    description = Column(TEXT)
    category_id = Column(String(36))  # FK to product_categories
    nafdac_number = Column(String(100), unique=True, nullable=False)
    batch_number = Column(String(100))
    manufacturer_name = Column(String(255))
    manufacturing_date = Column(Date)
    expiry_date = Column(Date)
    ingredients = Column(TEXT)
    warnings = Column(TEXT)
    image_urls = Column(String)  # Array
    master_artwork_url = Column(TEXT)
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.ACTIVE)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(String(36))  # FK to users
    
    __table_args__ = (
        Index("idx_products_company", "company_id"),
        Index("idx_products_nafdac", "nafdac_number"),
        Index("idx_products_status", "status"),
    )


class ProductBarcode(Base):
    """Product barcodes table"""
    __tablename__ = "product_barcodes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id = Column(String(36), nullable=False)  # FK to products
    barcode_type = Column(SQLEnum(BarcodeType))
    barcode_value = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        Index("idx_product_barcodes_value", "barcode_value"),
    )


class ProductEmbedding(Base):
    """Product embeddings table (AI fingerprints)"""
    __tablename__ = "product_embeddings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    product_id = Column(String(36), nullable=False)  # FK to products
    embedding_type = Column(SQLEnum(EmbeddingType), nullable=False)
    embedding_vector = Column(LargeBinary)
    model_version = Column(String(50))
    confidence_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_product_embeddings_product", "product_id"),
        Index("idx_product_embeddings_type", "embedding_type"),
    )
