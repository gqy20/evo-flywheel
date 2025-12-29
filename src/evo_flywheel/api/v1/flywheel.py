"""飞轮控制 API 端点

提供飞轮触发、状态查询和调度控制功能
"""

from datetime import datetime
from threading import Lock
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from evo_flywheel.logging import get_logger
from evo_flywheel.scheduler import run_daily_flywheel, schedule_flywheel

logger = get_logger(__name__)

router = APIRouter()

# 全局调度器状态
_scheduler_lock = Lock()
_scheduler_instance: Any = None
_scheduler_status: dict[str, bool | str | None] = {
    "running": False,
    "last_run": None,
    "next_run": None,
}


class FlywheelTriggerResponse(BaseModel):
    """飞轮触发响应"""

    collected: int = Field(description="采集的论文数量")
    analyzed: int = Field(description="分析的论文数量")
    report_generated: bool = Field(description="是否生成了报告")


class FlywheelStatusResponse(BaseModel):
    """飞轮状态响应"""

    running: bool = Field(description="调度器是否运行中")
    last_run: str | None = Field(description="上次运行时间", default=None)
    next_run: str | None = Field(description="下次运行时间", default=None)


class ScheduleControlRequest(BaseModel):
    """调度控制请求"""

    action: str = Field(description="操作: start 或 stop")


class ScheduleControlResponse(BaseModel):
    """调度控制响应"""

    status: str = Field(description="操作后的状态: started 或 stopped")


@router.post("/trigger", response_model=FlywheelTriggerResponse)
async def trigger_flywheel() -> FlywheelTriggerResponse:
    """手动触发一次飞轮运行

    执行完整流程：采集 -> 分析 -> 报告生成
    """
    try:
        logger.info("Manual flywheel trigger requested")
        result = run_daily_flywheel()

        # 更新状态
        with _scheduler_lock:
            _scheduler_status["last_run"] = datetime.now().isoformat()

        return FlywheelTriggerResponse(**result)

    except Exception as e:
        logger.error(f"Flywheel trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=FlywheelStatusResponse)
async def get_flywheel_status() -> FlywheelStatusResponse:
    """获取飞轮运行状态

    返回调度器运行状态、上次运行时间和下次运行时间
    """
    with _scheduler_lock:
        return FlywheelStatusResponse(
            running=_scheduler_status["running"],
            last_run=_scheduler_status["last_run"],
            next_run=_scheduler_status["next_run"],
        )


def _get_scheduler() -> Any:
    """获取全局调度器实例"""
    global _scheduler_instance
    with _scheduler_lock:
        if _scheduler_instance is None:
            _scheduler_instance = schedule_flywheel(interval_hours=4)
        return _scheduler_instance


@router.post("/schedule", response_model=ScheduleControlResponse)
async def control_schedule(request: ScheduleControlRequest) -> ScheduleControlResponse:
    """控制调度器

    启动或停止飞轮调度器

    Args:
        request: 调度控制请求

    Returns:
        ScheduleControlResponse: 操作结果
    """
    global _scheduler_instance

    if request.action == "start":
        with _scheduler_lock:
            if _scheduler_status["running"]:
                raise HTTPException(status_code=400, detail="调度器已在运行中")

            try:
                _scheduler_instance = _get_scheduler()
                if hasattr(_scheduler_instance, "running") and not _scheduler_instance.running:
                    _scheduler_instance.start()

                _scheduler_status["running"] = True
                _scheduler_status["next_run"] = datetime.now().isoformat()

                logger.info("Flywheel scheduler started")
                return ScheduleControlResponse(status="started")

            except Exception as e:
                logger.error(f"Failed to start scheduler: {e}")
                raise HTTPException(status_code=500, detail=f"启动调度器失败: {e}")

    elif request.action == "stop":
        with _scheduler_lock:
            # 检查是否真的在运行
            is_running = _scheduler_status["running"] or (
                _scheduler_instance is not None
                and hasattr(_scheduler_instance, "running")
                and _scheduler_instance.running
            )
            if not is_running:
                raise HTTPException(status_code=400, detail="调度器未运行")

            try:
                if _scheduler_instance is not None:
                    if hasattr(_scheduler_instance, "running") and _scheduler_instance.running:
                        _scheduler_instance.shutdown(wait=False)
                    _scheduler_instance = None

                _scheduler_status["running"] = False
                _scheduler_status["next_run"] = None

                logger.info("Flywheel scheduler stopped")
                return ScheduleControlResponse(status="stopped")

            except Exception as e:
                logger.error(f"Failed to stop scheduler: {e}")
                raise HTTPException(status_code=500, detail=f"停止调度器失败: {e}")

    else:
        raise HTTPException(status_code=400, detail=f"无效的操作: {request.action}")
