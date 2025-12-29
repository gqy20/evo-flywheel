"""FastAPI 主应用模块"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from evo_flywheel.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Evo-Flywheel API",
    description="进化生物学学术文献分析系统",
    version="0.7.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根端点，返回 API 基本信息"""
    return {"message": "Evo-Flywheel API", "docs": "/api/v1/docs"}


@app.get("/api/v1/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("FastAPI 应用启动")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("FastAPI 应用关闭")
