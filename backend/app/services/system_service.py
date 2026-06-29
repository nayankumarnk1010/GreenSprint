from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from sqlalchemy import inspect
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


class SystemService:
    """
    Final backend health and integration service.

    This checks:
    - Database connection
    - Database-backed modules 1 to 12
    - Service/API/AI modules 13 to 16
    - Important table counts
    - Local AI runtime availability
    """

    DATABASE_MODULES = [
        {
            "module_number": 1,
            "module_name": "Action Submission System",
            "tables": [
                "submissions",
                "submission_media",
            ],
        },
        {
            "module_number": 2,
            "module_name": "AI Verification & Fraud Detection",
            "tables": [
                "ai_verifications",
                "fraud_checks",
            ],
        },
        {
            "module_number": 3,
            "module_name": "AI Plant Health & Disease Detection",
            "tables": [
                "plant_diagnoses",
                "plant_care_recommendations",
            ],
        },
        {
            "module_number": 4,
            "module_name": "Environmental Impact Engine",
            "tables": [
                "impact_metrics",
                "user_impact_summaries",
                "challenge_impact_summaries",
            ],
        },
        {
            "module_number": 5,
            "module_name": "Gamification & Rewards System",
            "tables": [
                "points_ledger",
                "badges",
                "user_badges",
                "user_gamification_profiles",
                "leaderboard_snapshots",
            ],
        },
        {
            "module_number": 6,
            "module_name": "Sustainability Analytics System",
            "tables": [
                "submissions",
                "impact_metrics",
                "user_impact_summaries",
                "challenge_impact_summaries",
            ],
        },
        {
            "module_number": 7,
            "module_name": "Geospatial Green Impact Mapping",
            "tables": [
                "submissions",
                "impact_metrics",
            ],
        },
        {
            "module_number": 8,
            "module_name": "Community & Social Feed System",
            "tables": [
                "community_posts",
                "community_comments",
                "community_likes",
                "community_reports",
                "community_post_media",
            ],
        },
        {
            "module_number": 9,
            "module_name": "Organization & Campaign Management",
            "tables": [
                "organization_profiles",
                "campaigns",
                "campaign_members",
                "campaign_challenges",
            ],
        },
        {
            "module_number": 10,
            "module_name": "Notification System",
            "tables": [
                "notifications",
                "notification_preferences",
            ],
        },
        {
            "module_number": 11,
            "module_name": "ESG / Sustainability Reporting",
            "tables": [
                "esg_reports",
                "esg_report_metrics",
            ],
        },
        {
            "module_number": 12,
            "module_name": "Admin Moderation & Platform Control",
            "tables": [
                "admin_audit_logs",
                "platform_settings",
            ],
        },
    ]

    SERVICE_MODULES = [
        {
            "module_number": 13,
            "module_name": "Final Backend Integration",
            "checks": {
                "system_schema": "app/schemas/system.py",
                "system_service": "app/services/system_service.py",
                "system_endpoint": "app/api/v1/endpoints/system.py",
            },
        },
        {
            "module_number": 14,
            "module_name": "Local AI + Ollama + RAG + Multilingual + Audio",
            "checks": {
                "ollama_client": "app/services/ai/ollama_client.py",
                "rag_service": "app/services/ai/rag_service.py",
                "greensprint_ai_service": "app/services/ai/greensprint_ai_service.py",
                "localized_response_service": "app/services/ai/localized_response_service.py",
                "audio_service": "app/services/ai/audio_service.py",
                "ai_assistant_endpoint": "app/api/v1/endpoints/ai_assistant.py",
                "knowledge_sustainability": "app/ai/knowledge/sustainability_guidelines.md",
                "knowledge_tree": "app/ai/knowledge/tree_plantation.md",
                "knowledge_recycling": "app/ai/knowledge/recycling.md",
                "knowledge_water": "app/ai/knowledge/water_conservation.md",
                "knowledge_esg": "app/ai/knowledge/esg_reporting.md",
            },
            "runtime_check": "ollama",
        },
        {
            "module_number": 15,
            "module_name": "Image AI Upgrade for Submission Proof Verification",
            "checks": {
                "ai_vision_schema": "app/schemas/ai_vision.py",
                "local_vision_service": "app/services/ai/local_vision_service.py",
                "ai_vision_endpoint": "app/api/v1/endpoints/ai_vision.py",
            },
        },
        {
            "module_number": 16,
            "module_name": "Pretrained Plant Disease AI + Treatment + Guide Assistant",
            "checks": {
                "plant_ai_schema": "app/schemas/plant_ai.py",
                "plant_ai_endpoint": "app/api/v1/endpoints/plant_ai.py",
                "plant_disease_ai_service": "app/services/ai/plant_disease_ai_service.py",
                "plant_treatments": "app/ai/knowledge/plant_treatments.json",
                "plant_model": "models/plant_disease/mobilenetv2_plant.pth",
                "plant_class_names": "models/plant_disease/class_names.json",
            },
        },
    ]

    COUNT_TABLES = {
        "users": "users",
        "challenges": "challenges",
        "submissions": "submissions",
        "ai_verifications": "ai_verifications",
        "plant_diagnoses": "plant_diagnoses",
        "impact_metrics": "impact_metrics",
        "points_ledger_entries": "points_ledger",
        "community_posts": "community_posts",
        "organizations": "organization_profiles",
        "campaigns": "campaigns",
        "notifications": "notifications",
        "esg_reports": "esg_reports",
        "admin_audit_logs": "admin_audit_logs",
        "platform_settings": "platform_settings",
    }

    @staticmethod
    def ping() -> dict:
        return {
            "status": "OK",
            "message": "GreenSprint backend is running.",
            "app_name": settings.APP_NAME,
            "checked_at": datetime.utcnow(),
        }

    @staticmethod
    def _database_health(
        db: Session,
    ) -> dict:
        try:
            db.execute(
                text("SELECT 1")
            )

            return {
                "status": "OK",
                "message": "Database connection is healthy.",
                "database_url": settings.DATABASE_URL,
            }

        except Exception as exc:
            return {
                "status": "ERROR",
                "message": f"Database connection failed: {exc}",
                "database_url": settings.DATABASE_URL,
            }

    @staticmethod
    def _get_existing_tables(
        db: Session,
    ) -> set[str]:
        inspector = inspect(
            db.bind
        )

        return set(
            inspector.get_table_names()
        )

    @staticmethod
    def _check_database_module(
        module: dict,
        existing_tables: set[str],
    ) -> dict:
        required_tables = module["tables"]

        missing_tables = [
            table
            for table in required_tables
            if table not in existing_tables
        ]

        tables_found = len(
            required_tables
        ) - len(
            missing_tables
        )

        status = (
            "COMPLETE"
            if not missing_tables
            else "INCOMPLETE"
        )

        return {
            "module_number": module["module_number"],
            "module_name": module["module_name"],
            "status": status,
            "tables_required": len(required_tables),
            "tables_found": tables_found,
            "missing_tables": missing_tables,
            "checks_required": 0,
            "checks_found": 0,
            "missing_checks": [],
            "details": {
                "module_type": "database",
            },
        }

    @staticmethod
    def _check_path(
        path: str,
    ) -> bool:
        return Path(
            path
        ).exists()

    @staticmethod
    def _check_ollama_runtime() -> dict:
        base_url = getattr(
            settings,
            "OLLAMA_BASE_URL",
            "http://127.0.0.1:11434",
        )

        model_name = getattr(
            settings,
            "OLLAMA_MODEL",
            "llama3.2:3b",
        )

        url = f"{base_url}/api/tags"

        try:
            with urlopen(
                url,
                timeout=5,
            ) as response:
                status_code = response.status

            return {
                "available": status_code == 200,
                "base_url": base_url,
                "model": model_name,
                "message": "Ollama runtime is reachable.",
            }

        except URLError as exc:
            return {
                "available": False,
                "base_url": base_url,
                "model": model_name,
                "message": f"Ollama runtime is not reachable: {exc}",
            }

        except Exception as exc:
            return {
                "available": False,
                "base_url": base_url,
                "model": model_name,
                "message": f"Ollama runtime check failed: {exc}",
            }

    @staticmethod
    def _check_service_module(
        module: dict,
    ) -> dict:
        checks = module.get(
            "checks",
            {},
        )

        missing_checks = [
            check_name
            for check_name, path in checks.items()
            if not SystemService._check_path(path)
        ]

        checks_found = len(
            checks
        ) - len(
            missing_checks
        )

        details: dict[str, Any] = {
            "module_type": "service_ai_api",
            "checked_files": checks,
        }

        status = (
            "COMPLETE"
            if not missing_checks
            else "INCOMPLETE"
        )

        if module.get("runtime_check") == "ollama":
            ollama_status = SystemService._check_ollama_runtime()
            details["ollama_runtime"] = ollama_status

            if not ollama_status["available"]:
                status = (
                    "WARNING"
                    if status == "COMPLETE"
                    else "INCOMPLETE"
                )

        return {
            "module_number": module["module_number"],
            "module_name": module["module_name"],
            "status": status,
            "tables_required": 0,
            "tables_found": 0,
            "missing_tables": [],
            "checks_required": len(checks),
            "checks_found": checks_found,
            "missing_checks": missing_checks,
            "details": details,
        }

    @staticmethod
    def _count_table(
        db: Session,
        table_name: str,
        existing_tables: set[str],
    ) -> int:
        if table_name not in existing_tables:
            return 0

        try:
            result = db.execute(
                text(
                    f"SELECT COUNT(*) FROM {table_name}"
                )
            )

            return int(
                result.scalar() or 0
            )

        except Exception:
            return 0

    @staticmethod
    def _get_counts(
        db: Session,
        existing_tables: set[str],
    ) -> dict[str, int]:
        return {
            label: SystemService._count_table(
                db=db,
                table_name=table_name,
                existing_tables=existing_tables,
            )
            for label, table_name in SystemService.COUNT_TABLES.items()
        }

    @staticmethod
    def _module_summary(
        modules: list[dict],
    ) -> dict:
        complete_modules = len(
            [
                module
                for module in modules
                if module["status"] == "COMPLETE"
            ]
        )

        warning_modules = len(
            [
                module
                for module in modules
                if module["status"] == "WARNING"
            ]
        )

        incomplete_modules = len(
            [
                module
                for module in modules
                if module["status"] == "INCOMPLETE"
            ]
        )

        return {
            "total_modules": len(modules),
            "complete_modules": complete_modules,
            "warning_modules": warning_modules,
            "incomplete_modules": incomplete_modules,
            "modules": modules,
        }

    @staticmethod
    def health(
        db: Session,
    ) -> dict:
        database = SystemService._database_health(
            db=db,
        )

        existing_tables = SystemService._get_existing_tables(
            db=db,
        )

        modules = []

        for module in SystemService.DATABASE_MODULES:
            modules.append(
                SystemService._check_database_module(
                    module=module,
                    existing_tables=existing_tables,
                )
            )

        for module in SystemService.SERVICE_MODULES:
            modules.append(
                SystemService._check_service_module(
                    module=module,
                )
            )

        has_incomplete = any(
            module["status"] == "INCOMPLETE"
            for module in modules
        )

        has_warning = any(
            module["status"] == "WARNING"
            for module in modules
        )

        if database["status"] != "OK" or has_incomplete:
            status = "ERROR"

        elif has_warning:
            status = "WARNING"

        else:
            status = "OK"

        return {
            "status": status,
            "database": database,
            "modules": modules,
            "checked_at": datetime.utcnow(),
        }

    @staticmethod
    def integration_summary(
        db: Session,
    ) -> dict:
        health = SystemService.health(
            db=db,
        )

        existing_tables = SystemService._get_existing_tables(
            db=db,
        )

        counts = SystemService._get_counts(
            db=db,
            existing_tables=existing_tables,
        )

        ai_runtime = {
            "ollama": SystemService._check_ollama_runtime(),
            "plant_ai_model_available": Path(
                "models/plant_disease/mobilenetv2_plant.pth"
            ).exists(),
            "plant_ai_class_names_available": Path(
                "models/plant_disease/class_names.json"
            ).exists(),
            "local_vision_service_available": Path(
                "app/services/ai/local_vision_service.py"
            ).exists(),
            "rag_knowledge_base_available": Path(
                "app/ai/knowledge/sustainability_guidelines.md"
            ).exists(),
        }

        return {
            "status": health["status"],
            "database": health["database"],
            "module_status": SystemService._module_summary(
                modules=health["modules"],
            ),
            "counts": counts,
            "ai_runtime": ai_runtime,
            "checked_at": datetime.utcnow(),
        }