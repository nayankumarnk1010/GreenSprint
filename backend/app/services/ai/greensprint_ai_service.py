import json
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.ai.languages import SUPPORTED_LANGUAGES
from app.ai.languages import normalize_language
from app.core.config import settings
from app.models.admin_audit_log import AdminAuditLog
from app.models.ai_verification import AIVerification
from app.models.campaign import Campaign
from app.models.community_post import CommunityPost
from app.models.esg_report import ESGReport
from app.models.impact_metric import ImpactMetric
from app.models.notification import Notification
from app.models.organization_profile import OrganizationProfile
from app.models.plant_diagnosis import PlantDiagnosis
from app.models.platform_setting import PlatformSetting
from app.models.submission import Submission
from app.models.user import User
from app.services.ai.audio_service import AudioService
from app.services.ai.localized_response_service import LocalizedResponseService
from app.services.ai.ollama_client import OllamaClient
from app.services.ai.rag_service import RAGService


class GreenSprintAIService:
    @staticmethod
    def supported_languages() -> list[dict]:
        return [
            {
                "code": code,
                "name": details["name"],
                "native_name": details["native_name"],
            }
            for code, details in SUPPORTED_LANGUAGES.items()
        ]

    @staticmethod
    def _model_used(
        response_source: str,
    ) -> str:
        if "ollama" in response_source:
            return settings.OLLAMA_MODEL

        return "rule_based_fallback"

    @staticmethod
    def _system_prompt(
        language: str,
    ) -> str:
        language = normalize_language(language)

        language_rules = {
            "en": (
                "Respond only in simple English. "
                "Use short sentences and practical bullet points."
            ),
            "kn": (
                "Respond only in Kannada using Kannada script. "
                "Use simple daily Kannada words. "
                "Do not use complex or unnatural translated words. "
                "Give practical points that a student or normal user can follow."
            ),
            "hi": (
                "Respond only in Hindi using Devanagari script. "
                "Use simple daily Hindi words. "
                "Give practical points that a student or normal user can follow."
            ),
            "ta": (
                "Respond only in Tamil using Tamil script. "
                "Use simple daily Tamil words. "
                "Give practical points that a student or normal user can follow."
            ),
            "te": (
                "Respond only in Telugu using Telugu script. "
                "Use simple daily Telugu words. "
                "Give practical points that a student or normal user can follow."
            ),
        }

        return f"""
You are GreenSprint AI Assistant.

GreenSprint is an AI-powered sustainability platform.
You help users, organizations, and admins understand eco-actions,
impact metrics, ESG reports, campaigns, sustainability challenges,
and environmental best practices.

Important rules:
1. Give practical, safe, non-harmful sustainability guidance.
2. Do not invent platform data.
3. If database values are provided, explain only from those values.
4. Keep the answer short, clear, and useful.
5. Prefer 3 to 5 bullet points when giving suggestions.
6. Avoid long paragraphs.
7. {language_rules.get(language, language_rules["en"])}
"""

    @staticmethod
    def _generate_audio_if_required(
        text: str,
        language: str,
        audio_enabled: bool,
    ) -> str | None:
        if not audio_enabled:
            return None

        return AudioService.generate_audio(
            text=text,
            language=language,
        )

    @staticmethod
    def _fallback_chat_answer(
        message: str,
        language: str,
    ) -> str:
        language = normalize_language(language)

        fallback_answers = {
            "en": (
                "Ollama is not running, so this is a fallback answer. "
                "GreenSprint helps users complete eco-actions such as tree plantation, "
                "recycling, water conservation, waste cleanup, and sustainable transport. "
                "Try choosing one small action, upload real proof, and track your impact."
            ),
            "hi": (
                "Ollama अभी चल नहीं रहा है, इसलिए यह fallback उत्तर है। "
                "GreenSprint उपयोगकर्ताओं को tree plantation, recycling, water conservation, "
                "waste cleanup और sustainable transport जैसे eco-actions पूरा करने में मदद करता है।"
            ),
            "kn": (
                "Ollama ಈಗ ಚಾಲನೆಯಲ್ಲಿಲ್ಲ, ಆದ್ದರಿಂದ ಇದು fallback ಉತ್ತರವಾಗಿದೆ. "
                "GreenSprint ಬಳಕೆದಾರರಿಗೆ ಮರ ನೆಡುವುದು, recycling, ನೀರು ಉಳಿಸುವುದು, "
                "waste cleanup ಮತ್ತು sustainable transport ಮುಂತಾದ eco-actions ಮಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ."
            ),
            "ta": (
                "Ollama தற்போது இயங்கவில்லை, எனவே இது fallback பதில். "
                "GreenSprint பயனர்களுக்கு மரநடுதல், recycling, water conservation, "
                "waste cleanup மற்றும் sustainable transport போன்ற eco-actions செய்ய உதவுகிறது."
            ),
            "te": (
                "Ollama ప్రస్తుతం పనిచేయడం లేదు, అందుకే ఇది fallback సమాధానం. "
                "GreenSprint వినియోగదారులకు tree plantation, recycling, water conservation, "
                "waste cleanup మరియు sustainable transport వంటి eco-actions చేయడంలో సహాయపడుతుంది."
            ),
        }

        return fallback_answers.get(
            language,
            fallback_answers["en"],
        )

    @staticmethod
    def chat(
        message: str,
        language: str = "en",
        audio_enabled: bool = False,
    ) -> dict:
        language = normalize_language(language)

        context, sources = RAGService.build_context(
            query=message,
        )

        prompt = f"""
Use the following GreenSprint knowledge base context to answer the user.

Context:
{context}

User question:
{message}

Answer requirements:
- Give a direct answer.
- Give 3 to 5 practical points.
- Use simple words.
- Avoid technical or awkward translated words.
- Do not mention that you are using context.
- Do not give unrelated information.
"""

        success, answer = OllamaClient.generate(
            prompt=prompt,
            system_prompt=GreenSprintAIService._system_prompt(language),
            temperature=0.3,
        )

        response_source = "ollama"

        localized_answer = LocalizedResponseService.get_chat_answer(
            message=message,
            language=language,
        )

        if language != "en" and localized_answer:
            answer = localized_answer

            if success:
                response_source = "ollama_plus_localized_template"
            else:
                response_source = "localized_template_fallback"

        elif not success:
            answer = GreenSprintAIService._fallback_chat_answer(
                message=message,
                language=language,
            )
            response_source = "fallback"

        audio_url = GreenSprintAIService._generate_audio_if_required(
            text=answer,
            language=language,
            audio_enabled=audio_enabled,
        )

        return {
            "answer": answer,
            "language": language,
            "model_used": GreenSprintAIService._model_used(response_source),
            "response_source": response_source,
            "context_used": sources,
            "audio_url": audio_url,
            "created_at": datetime.utcnow(),
        }

    @staticmethod
    def generate_challenge(
        prompt: str,
        category: str | None = None,
        difficulty: str | None = None,
        language: str = "en",
        audio_enabled: bool = False,
    ) -> dict:
        language = normalize_language(language)

        ai_prompt = f"""
Generate one sustainability challenge for GreenSprint.

User request:
{prompt}

Preferred category:
{category or "Not specified"}

Preferred difficulty:
{difficulty or "Not specified"}

Return only valid JSON with this structure:
{{
  "title": "...",
  "description": "...",
  "category": "...",
  "difficulty": "...",
  "suggested_points": 100,
  "rules": ["...", "...", "..."]
}}
"""

        success, answer = OllamaClient.generate(
            prompt=ai_prompt,
            system_prompt=GreenSprintAIService._system_prompt(language),
            temperature=0.4,
        )

        response_source = "ollama"

        try:
            cleaned_answer = answer.strip()

            if cleaned_answer.startswith("```"):
                cleaned_answer = cleaned_answer.replace("```json", "")
                cleaned_answer = cleaned_answer.replace("```", "")
                cleaned_answer = cleaned_answer.strip()

            parsed = json.loads(cleaned_answer)

        except Exception:
            parsed = {
                "title": "Plastic-Free Day Challenge",
                "description": (
                    "Avoid single-use plastic for one day and upload real proof "
                    "of your eco-friendly alternative."
                ),
                "category": category or "WASTE_REDUCTION",
                "difficulty": difficulty or "EASY",
                "suggested_points": 100,
                "rules": [
                    "Avoid single-use plastic.",
                    "Use reusable bottle or bag.",
                    "Upload clear proof of your action.",
                ],
            }

            if success:
                response_source = "ollama_parse_fallback"
            else:
                response_source = "fallback"

        challenge_text = (
            f"{parsed.get('title', '')}. "
            f"{parsed.get('description', '')}. "
            f"Rules: {', '.join(parsed.get('rules', []))}"
        )

        audio_url = GreenSprintAIService._generate_audio_if_required(
            text=challenge_text,
            language=language,
            audio_enabled=audio_enabled,
        )

        return {
            "title": parsed.get("title", "Eco Challenge"),
            "description": parsed.get("description", ""),
            "category": parsed.get("category", category or "GENERAL"),
            "difficulty": parsed.get("difficulty", difficulty or "EASY"),
            "suggested_points": int(parsed.get("suggested_points", 100)),
            "rules": parsed.get("rules", []),
            "language": language,
            "model_used": GreenSprintAIService._model_used(response_source),
            "response_source": response_source,
            "audio_url": audio_url,
            "created_at": datetime.utcnow(),
        }

    @staticmethod
    def explain_impact(
        db: Session,
        submission_id: str,
        language: str = "en",
        audio_enabled: bool = False,
    ) -> dict:
        language = normalize_language(language)

        impact = (
            db.query(ImpactMetric)
            .filter(ImpactMetric.submission_id == submission_id)
            .first()
        )

        if not impact:
            explanation = "No impact metric was found for this submission."

            audio_url = GreenSprintAIService._generate_audio_if_required(
                text=explanation,
                language=language,
                audio_enabled=audio_enabled,
            )

            return {
                "explanation": explanation,
                "language": language,
                "model_used": "rule_based_fallback",
                "response_source": "fallback",
                "audio_url": audio_url,
                "created_at": datetime.utcnow(),
            }

        metric_type = str(
            getattr(
                impact,
                "metric_type",
                "Unknown",
            )
        )

        calculation_status = str(
            getattr(
                impact,
                "calculation_status",
                "Unknown",
            )
        )

        co2e_saved_kg = getattr(
            impact,
            "co2e_saved_kg",
            0,
        ) or 0

        trees_planted = getattr(
            impact,
            "trees_planted",
            0,
        ) or 0

        water_saved_liters = getattr(
            impact,
            "water_saved_liters",
            0,
        ) or 0

        waste_reduced_kg = getattr(
            impact,
            "waste_reduced_kg",
            0,
        ) or 0

        energy_saved_kwh = getattr(
            impact,
            "energy_saved_kwh",
            0,
        ) or 0

        biodiversity_score = getattr(
            impact,
            "biodiversity_score",
            0,
        ) or 0

        confidence_score = getattr(
            impact,
            "confidence_score",
            0,
        ) or 0

        prompt = f"""
Explain this GreenSprint impact result in simple words.

Impact data:
Metric type: {metric_type}
Calculation status: {calculation_status}
CO2e saved kg: {co2e_saved_kg}
Trees planted: {trees_planted}
Water saved liters: {water_saved_liters}
Waste reduced kg: {waste_reduced_kg}
Energy saved kWh: {energy_saved_kwh}
Biodiversity score: {biodiversity_score}
Confidence score: {confidence_score}

Explain what this means for the user.
Keep it short and practical.
"""

        success, explanation = OllamaClient.generate(
            prompt=prompt,
            system_prompt=GreenSprintAIService._system_prompt(language),
            temperature=0.3,
        )

        response_source = "ollama"

        if not success:
            explanation = (
                "This activity created measurable environmental impact. "
                f"Estimated CO2e saved is {co2e_saved_kg} kg, "
                f"trees planted is {trees_planted}, "
                f"biodiversity score is {biodiversity_score}, "
                f"and confidence score is {confidence_score}."
            )
            response_source = "fallback"

        audio_url = GreenSprintAIService._generate_audio_if_required(
            text=explanation,
            language=language,
            audio_enabled=audio_enabled,
        )

        return {
            "explanation": explanation,
            "language": language,
            "model_used": GreenSprintAIService._model_used(response_source),
            "response_source": response_source,
            "audio_url": audio_url,
            "created_at": datetime.utcnow(),
        }

    @staticmethod
    def explain_esg_report(
        db: Session,
        report_id: str,
        language: str = "en",
        audio_enabled: bool = False,
    ) -> dict:
        language = normalize_language(language)

        report = (
            db.query(ESGReport)
            .filter(ESGReport.id == report_id)
            .first()
        )

        if not report:
            explanation = "ESG report was not found."

            audio_url = GreenSprintAIService._generate_audio_if_required(
                text=explanation,
                language=language,
                audio_enabled=audio_enabled,
            )

            return {
                "explanation": explanation,
                "language": language,
                "model_used": "rule_based_fallback",
                "response_source": "fallback",
                "audio_url": audio_url,
                "created_at": datetime.utcnow(),
            }

        raw_summary = report.summary_json or {}

        if isinstance(raw_summary, str):
            try:
                summary = json.loads(raw_summary)
            except Exception:
                summary = {}
        else:
            summary = raw_summary

        environmental = summary.get("environmental", {})
        social = summary.get("social", {})
        governance = summary.get("governance", {})
        engagement = summary.get("engagement", {})
        verification = summary.get("verification", {})

        total_co2e_saved_kg = environmental.get(
            "total_co2e_saved_kg",
            0,
        ) or 0

        total_trees_planted = environmental.get(
            "total_trees_planted",
            0,
        ) or 0

        total_biodiversity_score = environmental.get(
            "total_biodiversity_score",
            0,
        ) or 0

        impact_actions_count = environmental.get(
            "impact_actions_count",
            0,
        ) or 0

        campaigns_count = social.get(
            "campaigns_count",
            0,
        ) or 0

        active_campaigns_count = social.get(
            "active_campaigns_count",
            0,
        ) or 0

        campaign_members_count = social.get(
            "campaign_members_count",
            0,
        ) or 0

        unique_participants_count = social.get(
            "unique_participants_count",
            0,
        ) or 0

        linked_challenges_count = governance.get(
            "linked_challenges_count",
            0,
        ) or 0

        submissions_count = governance.get(
            "submissions_count",
            0,
        ) or 0

        published_reports_count = governance.get(
            "published_reports_count",
            0,
        ) or 0

        data_sources = governance.get(
            "data_sources",
            [],
        ) or []

        community_posts_count = engagement.get(
            "community_posts_count",
            0,
        ) or 0

        points_awarded = engagement.get(
            "points_awarded",
            0,
        ) or 0

        ai_verifications_count = verification.get(
            "ai_verifications_count",
            0,
        ) or 0

        verification_coverage_percent = verification.get(
            "verification_coverage_percent",
            0,
        ) or 0

        average_ai_confidence = verification.get(
            "average_ai_confidence",
            0,
        ) or 0

        average_fraud_risk = verification.get(
            "average_fraud_risk",
            0,
        ) or 0

        exact_explanation = (
            f"ESG Report Summary: {report.title}\n\n"
            f"Environmental Performance:\n"
            f"• Total CO2e saved: {total_co2e_saved_kg} kg\n"
            f"• Trees planted: {total_trees_planted}\n"
            f"• Biodiversity score: {total_biodiversity_score}\n"
            f"• Impact actions recorded: {impact_actions_count}\n\n"
            f"Social Performance:\n"
            f"• Total campaigns: {campaigns_count}\n"
            f"• Active campaigns: {active_campaigns_count}\n"
            f"• Campaign members: {campaign_members_count}\n"
            f"• Unique participants: {unique_participants_count}\n"
            f"• Community posts: {community_posts_count}\n"
            f"• Points awarded: {points_awarded}\n\n"
            f"Governance Performance:\n"
            f"• Linked challenges: {linked_challenges_count}\n"
            f"• Submissions reviewed: {submissions_count}\n"
            f"• Published reports: {published_reports_count}\n"
            f"• AI verifications: {ai_verifications_count}\n"
            f"• Verification coverage: {verification_coverage_percent}%\n"
            f"• Average AI confidence: {average_ai_confidence}\n"
            f"• Average fraud risk: {average_fraud_risk}\n\n"
            f"Data Sources:\n"
            f"{', '.join(data_sources) if data_sources else 'No data sources listed.'}\n\n"
            f"Recommendations:\n"
            f"• Increase the number of eco-action submissions.\n"
            f"• Encourage more users to participate in campaigns.\n"
            f"• Continue AI verification and admin moderation for trust.\n"
            f"• Publish ESG reports regularly for better governance tracking."
        )

        prompt = f"""
You are reviewing an ESG report for GreenSprint.

Use these exact values only. Do not change, round, multiply, or convert them.

Exact ESG explanation:
{exact_explanation}

Important:
- If CO2e saved is 21.77 kg, write exactly 21.77 kg.
- If trees planted is 1, write exactly 1.
- Do not write 21,770 kg.
- Do not write 1,000 trees.
- Keep the explanation professional and simple.
"""

        success, _ai_explanation = OllamaClient.generate(
            prompt=prompt,
            system_prompt=GreenSprintAIService._system_prompt(language),
            temperature=0.1,
        )

        if success:
            response_source = "ollama_plus_exact_data_guard"
        else:
            response_source = "exact_data_fallback"

        explanation = exact_explanation

        audio_url = GreenSprintAIService._generate_audio_if_required(
            text=explanation,
            language=language,
            audio_enabled=audio_enabled,
        )

        return {
            "explanation": explanation,
            "language": language,
            "model_used": GreenSprintAIService._model_used(response_source),
            "response_source": response_source,
            "audio_url": audio_url,
            "created_at": datetime.utcnow(),
        }

    @staticmethod
    def admin_insights(
        db: Session,
        language: str = "en",
        audio_enabled: bool = False,
    ) -> dict:
        language = normalize_language(language)

        snapshot: dict[str, Any] = {
            "users": db.query(User).count(),
            "organizations": db.query(OrganizationProfile).count(),
            "campaigns": db.query(Campaign).count(),
            "submissions": db.query(Submission).count(),
            "ai_verifications": db.query(AIVerification).count(),
            "plant_diagnoses": db.query(PlantDiagnosis).count(),
            "impact_metrics": db.query(ImpactMetric).count(),
            "community_posts": db.query(CommunityPost).count(),
            "notifications": db.query(Notification).count(),
            "esg_reports": db.query(ESGReport).count(),
            "audit_logs": db.query(AdminAuditLog).count(),
            "platform_settings": db.query(PlatformSetting).count(),
        }

        prompt = f"""
Analyze this GreenSprint platform snapshot and give admin insights.

Platform snapshot:
{snapshot}

Generate:
1. Overall platform health
2. Important observations
3. Risks or pending work
4. Three recommendations

Keep it concise.
"""

        success, answer = OllamaClient.generate(
            prompt=prompt,
            system_prompt=GreenSprintAIService._system_prompt(language),
            temperature=0.3,
        )

        response_source = "ollama"

        if not success:
            answer = (
                "The platform is active and all main backend modules are connected. "
                "Admin should monitor AI verification reviews, increase community activity, "
                "and continue generating campaign-level ESG reports."
            )
            response_source = "fallback"

        recommendations = [
            "Review pending AI verification cases.",
            "Encourage more users to join campaigns.",
            "Generate regular ESG reports for organizations.",
        ]

        audio_url = GreenSprintAIService._generate_audio_if_required(
            text=answer,
            language=language,
            audio_enabled=audio_enabled,
        )

        return {
            "insight": answer,
            "recommendations": recommendations,
            "language": language,
            "model_used": GreenSprintAIService._model_used(response_source),
            "response_source": response_source,
            "audio_url": audio_url,
            "platform_snapshot": snapshot,
            "created_at": datetime.utcnow(),
        }