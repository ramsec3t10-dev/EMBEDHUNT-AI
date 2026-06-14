"""Connector interfaces for external job sources."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExternalJob:
    source_name: str
    source_job_id: str
    company_name: str
    title: str
    source_url: str | None = None
    location: str | None = None
    work_mode: str | None = None
    salary_min_lpa: float | None = None
    salary_max_lpa: float | None = None
    description: str | None = None
    required_skills: str | None = None


class JobConnector(Protocol):
    source_name: str

    async def fetch_jobs(self) -> list[ExternalJob]:
        """Fetch normalized jobs from one source."""


class MockEmbeddedJobConnector:
    source_name = "mock_embedded_feed"

    async def fetch_jobs(self) -> list[ExternalJob]:
        return [
            ExternalJob(
                source_name=self.source_name,
                source_job_id="mock-qualcomm-embedded-001",
                company_name="Qualcomm",
                title="Embedded Software Engineer",
                source_url="https://careers.qualcomm.com/",
                location="Bengaluru",
                work_mode="hybrid",
                salary_min_lpa=16,
                salary_max_lpa=22,
                description=(
                    "Develop embedded firmware for ARM based platforms with RTOS, "
                    "CAN, SPI, I2C, debugging, and automotive communication stacks."
                ),
                required_skills="Embedded C, RTOS, CAN, SPI, I2C, ARM Cortex",
            ),
            ExternalJob(
                source_name=self.source_name,
                source_job_id="mock-nvidia-firmware-001",
                company_name="NVIDIA",
                title="Senior Firmware Engineer",
                source_url="https://www.nvidia.com/en-us/about-nvidia/careers/",
                location="Hyderabad",
                work_mode="onsite",
                salary_min_lpa=28,
                salary_max_lpa=42,
                description=(
                    "Own firmware for high performance devices, Linux bring-up, "
                    "kernel debugging, and board validation."
                ),
                required_skills="Firmware, C++, Linux, Kernel, Device Driver, Debugging",
            ),
            ExternalJob(
                source_name=self.source_name,
                source_job_id="mock-bosch-autosar-001",
                company_name="Bosch",
                title="AUTOSAR Embedded Developer",
                source_url="https://www.bosch.com/careers/",
                location="Coimbatore",
                work_mode="hybrid",
                salary_min_lpa=12,
                salary_max_lpa=18,
                description=(
                    "Work on automotive embedded software, AUTOSAR modules, CAN, LIN, "
                    "diagnostics, and microcontroller integration."
                ),
                required_skills="AUTOSAR, Embedded C, CAN, LIN, Automotive, Microcontroller",
            ),
        ]
