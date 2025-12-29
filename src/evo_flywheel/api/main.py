"""FastAPI 主应用模块"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from evo_flywheel.api.v1 import collection, embeddings, papers, reports, search, stats
from evo_flywheel.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("FastAPI 应用启动")
    yield
    # 关闭
    logger.info("FastAPI 应用关闭")


app = FastAPI(
    title="Evo-Flywheel API",
    description="进化生物学学术文献分析系统",
    version="0.7.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan,
)

# CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 v1 路由
app.include_router(papers.router, prefix="/api/v1/papers", tags=["papers"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(collection.router, prefix="/api/v1/collection", tags=["collection"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["stats"])
app.include_router(embeddings.router, prefix="/api/v1/embeddings", tags=["embeddings"])


@app.get("/")
async def root():
    """根端点，返回 API 基本信息"""
    return {"message": "Evo-Flywheel API", "docs": "/api/v1/docs"}


@app.get("/api/v1/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}
