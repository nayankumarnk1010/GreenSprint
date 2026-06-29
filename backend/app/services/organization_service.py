from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.enums import CampaignChallengeStatus
from app.core.enums import CampaignMemberRole
from app.core.enums import CampaignMemberStatus
from app.core.enums import CampaignStatus
from app.core.enums import OrganizationProfileStatus
from app.core.enums import UserRole
from app.models.campaign import Campaign
from app.models.campaign_challenge import CampaignChallenge
from app.models.campaign_member import CampaignMember
from app.models.challenge import Challenge
from app.models.community_post import CommunityPost
from app.models.impact_metric import ImpactMetric
from app.models.organization_profile import OrganizationProfile
from app.models.submission import Submission
from app.models.user import User


class OrganizationService:
    @staticmethod
    def _is_admin(user: User) -> bool:
        return user.role == UserRole.ADMIN

    @staticmethod
    def _is_org_or_admin(user: User) -> bool:
        return user.role in {
            UserRole.ORGANIZATION,
            UserRole.ADMIN,
        }

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value or 0.0), 3)

    @staticmethod
    def _percent(value: float, target: float) -> float:
        if not target:
            return 0.0

        return round(min((float(value or 0.0) / float(target)) * 100, 100), 2)

    @staticmethod
    def _get_organization_by_user(
        db: Session,
        user_id: str,
    ) -> OrganizationProfile | None:
        return (
            db.query(OrganizationProfile)
            .filter(OrganizationProfile.user_id == user_id)
            .first()
        )

    @staticmethod
    def _get_organization(
        db: Session,
        organization_id: str,
    ) -> OrganizationProfile | None:
        return (
            db.query(OrganizationProfile)
            .filter(OrganizationProfile.id == organization_id)
            .first()
        )

    @staticmethod
    def _get_campaign(
        db: Session,
        campaign_id: str,
    ) -> Campaign | None:
        return (
            db.query(Campaign)
            .filter(Campaign.id == campaign_id)
            .first()
        )

    @staticmethod
    def _can_manage_organization(
        user: User,
        organization: OrganizationProfile,
    ) -> bool:
        if OrganizationService._is_admin(user):
            return True

        return organization.user_id == user.id

    @staticmethod
    def _can_manage_campaign(
        db: Session,
        user: User,
        campaign: Campaign,
    ) -> bool:
        if OrganizationService._is_admin(user):
            return True

        organization = OrganizationService._get_organization(
            db=db,
            organization_id=campaign.organization_id,
        )

        if not organization:
            return False

        return organization.user_id == user.id

    @staticmethod
    def create_my_profile(
        db: Session,
        current_user: User,
        payload,
    ) -> OrganizationProfile:
        if not OrganizationService._is_org_or_admin(current_user):
            raise PermissionError(
                "Only ORGANIZATION or ADMIN users can create organization profiles"
            )

        existing = OrganizationService._get_organization_by_user(
            db=db,
            user_id=current_user.id,
        )

        if existing:
            raise ValueError("Organization profile already exists for this user")

        profile = OrganizationProfile(
            user_id=current_user.id,
            organization_name=payload.organization_name,
            organization_type=payload.organization_type,
            description=payload.description,
            website_url=payload.website_url,
            contact_email=payload.contact_email or current_user.email,
            contact_phone=payload.contact_phone,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            status=OrganizationProfileStatus.ACTIVE,
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        return profile

    @staticmethod
    def get_my_profile(
        db: Session,
        current_user: User,
    ) -> OrganizationProfile:
        profile = OrganizationService._get_organization_by_user(
            db=db,
            user_id=current_user.id,
        )

        if not profile:
            raise ValueError("Organization profile not found")

        return profile

    @staticmethod
    def update_my_profile(
        db: Session,
        current_user: User,
        payload,
    ) -> OrganizationProfile:
        profile = OrganizationService.get_my_profile(
            db=db,
            current_user=current_user,
        )

        update_data = payload.model_dump(exclude_unset=True)

        if "status" in update_data and not OrganizationService._is_admin(current_user):
            update_data.pop("status")

        for key, value in update_data.items():
            setattr(profile, key, value)

        db.commit()
        db.refresh(profile)

        return profile

    @staticmethod
    def list_organizations(
        db: Session,
        current_user: User,
        limit: int = 50,
        offset: int = 0,
    ) -> list[OrganizationProfile]:
        query = db.query(OrganizationProfile)

        if not OrganizationService._is_admin(current_user):
            query = query.filter(
                OrganizationProfile.status == OrganizationProfileStatus.ACTIVE
            )

        return (
            query.order_by(OrganizationProfile.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_organization_public(
        db: Session,
        organization_id: str,
        current_user: User,
    ) -> OrganizationProfile:
        profile = OrganizationService._get_organization(
            db=db,
            organization_id=organization_id,
        )

        if not profile:
            raise ValueError("Organization profile not found")

        if (
            profile.status != OrganizationProfileStatus.ACTIVE
            and not OrganizationService._can_manage_organization(current_user, profile)
        ):
            raise PermissionError("You do not have permission to view this organization")

        return profile

    @staticmethod
    def _campaign_counts(
        db: Session,
        campaign_id: str,
    ) -> dict:
        members_count = (
            db.query(CampaignMember)
            .filter(CampaignMember.campaign_id == campaign_id)
            .filter(CampaignMember.status == CampaignMemberStatus.ACTIVE)
            .count()
        )

        challenges = (
            db.query(CampaignChallenge.challenge_id)
            .filter(CampaignChallenge.campaign_id == campaign_id)
            .filter(CampaignChallenge.status == CampaignChallengeStatus.ACTIVE)
            .all()
        )

        challenge_ids = [
            row[0]
            for row in challenges
        ]

        challenges_count = len(challenge_ids)

        submissions_count = 0

        if challenge_ids:
            submissions_count = (
                db.query(Submission)
                .filter(Submission.challenge_id.in_(challenge_ids))
                .count()
            )

        return {
            "members_count": members_count,
            "challenges_count": challenges_count,
            "submissions_count": submissions_count,
        }

    @staticmethod
    def _campaign_payload(
        db: Session,
        campaign: Campaign,
    ) -> dict:
        counts = OrganizationService._campaign_counts(
            db=db,
            campaign_id=campaign.id,
        )

        return {
            "id": campaign.id,
            "organization_id": campaign.organization_id,
            "created_by": campaign.created_by,
            "title": campaign.title,
            "description": campaign.description,
            "status": campaign.status,
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "target_participants": campaign.target_participants,
            "target_co2e_saved_kg": campaign.target_co2e_saved_kg,
            "target_trees_planted": campaign.target_trees_planted,
            "city": campaign.city,
            "state": campaign.state,
            "country": campaign.country,
            "members_count": counts["members_count"],
            "challenges_count": counts["challenges_count"],
            "submissions_count": counts["submissions_count"],
            "created_at": campaign.created_at,
            "updated_at": campaign.updated_at,
        }

    @staticmethod
    def create_campaign(
        db: Session,
        current_user: User,
        payload,
    ) -> dict:
        organization = OrganizationService.get_my_profile(
            db=db,
            current_user=current_user,
        )

        campaign = Campaign(
            organization_id=organization.id,
            created_by=current_user.id,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            start_date=payload.start_date,
            end_date=payload.end_date,
            target_participants=payload.target_participants,
            target_co2e_saved_kg=payload.target_co2e_saved_kg,
            target_trees_planted=payload.target_trees_planted,
            city=payload.city,
            state=payload.state,
            country=payload.country,
        )

        db.add(campaign)
        db.flush()

        owner_member = CampaignMember(
            campaign_id=campaign.id,
            user_id=current_user.id,
            role=CampaignMemberRole.OWNER,
            status=CampaignMemberStatus.ACTIVE,
        )

        db.add(owner_member)
        db.commit()
        db.refresh(campaign)

        return OrganizationService._campaign_payload(
            db=db,
            campaign=campaign,
        )

    @staticmethod
    def list_my_campaigns(
        db: Session,
        current_user: User,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        organization = OrganizationService.get_my_profile(
            db=db,
            current_user=current_user,
        )

        campaigns = (
            db.query(Campaign)
            .filter(Campaign.organization_id == organization.id)
            .order_by(Campaign.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [
            OrganizationService._campaign_payload(
                db=db,
                campaign=campaign,
            )
            for campaign in campaigns
        ]

    @staticmethod
    def list_public_campaigns(
        db: Session,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        campaigns = (
            db.query(Campaign)
            .filter(Campaign.status == CampaignStatus.ACTIVE)
            .order_by(Campaign.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [
            OrganizationService._campaign_payload(
                db=db,
                campaign=campaign,
            )
            for campaign in campaigns
        ]

    @staticmethod
    def get_campaign_detail(
        db: Session,
        campaign_id: str,
    ) -> dict:
        campaign = OrganizationService._get_campaign(
            db=db,
            campaign_id=campaign_id,
        )

        if not campaign:
            raise ValueError("Campaign not found")

        return OrganizationService._campaign_payload(
            db=db,
            campaign=campaign,
        )

    @staticmethod
    def update_campaign(
        db: Session,
        current_user: User,
        campaign_id: str,
        payload,
    ) -> dict:
        campaign = OrganizationService._get_campaign(
            db=db,
            campaign_id=campaign_id,
        )

        if not campaign:
            raise ValueError("Campaign not found")

        if not OrganizationService._can_manage_campaign(db, current_user, campaign):
            raise PermissionError("You do not have permission to update this campaign")

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(campaign, key, value)

        db.commit()
        db.refresh(campaign)

        return OrganizationService._campaign_payload(
            db=db,
            campaign=campaign,
        )

    @staticmethod
    def join_campaign(
        db: Session,
        current_user: User,
        campaign_id: str,
    ) -> CampaignMember:
        campaign = OrganizationService._get_campaign(
            db=db,
            campaign_id=campaign_id,
        )

        if not campaign:
            raise ValueError("Campaign not found")

        if campaign.status not in {
            CampaignStatus.ACTIVE,
            CampaignStatus.DRAFT,
        }:
            raise ValueError("This campaign is not open for joining")

        existing = (
            db.query(CampaignMember)
            .filter(CampaignMember.campaign_id == campaign_id)
            .filter(CampaignMember.user_id == current_user.id)
            .first()
        )

        if existing:
            existing.status = CampaignMemberStatus.ACTIVE
            existing.role = existing.role or CampaignMemberRole.PARTICIPANT
            db.commit()
            db.refresh(existing)
            return existing

        member = CampaignMember(
            campaign_id=campaign_id,
            user_id=current_user.id,
            role=CampaignMemberRole.PARTICIPANT,
            status=CampaignMemberStatus.ACTIVE,
        )

        db.add(member)
        db.commit()
        db.refresh(member)

        return member

    @staticmethod
    def add_campaign_member(
        db: Session,
        current_user: User,
        campaign_id: str,
        payload,
    ) -> CampaignMember:
        campaign = OrganizationService._get_campaign(
            db=db,
            campaign_id=campaign_id,
        )

        if not campaign:
            raise ValueError("Campaign not found")

        if not OrganizationService._can_manage_campaign(db, current_user, campaign):
            raise PermissionError("You do not have permission to add campaign members")

        user = (
            db.query(User)
            .filter(User.id == payload.user_id)
            .first()
        )

        if not user:
            raise ValueError("User not found")

        existing = (
            db.query(CampaignMember)
            .filter(CampaignMember.campaign_id == campaign_id)
            .filter(CampaignMember.user_id == payload.user_id)
            .first()
        )

        if existing:
            existing.role = payload.role
            existing.status = CampaignMemberStatus.ACTIVE
            db.commit()
            db.refresh(existing)
            return existing

        member = CampaignMember(
            campaign_id=campaign_id,
            user_id=payload.user_id,
            role=payload.role,
            status=CampaignMemberStatus.ACTIVE,
        )

        db.add(member)
        db.commit()
        db.refresh(member)

        return member

    @staticmethod
    def _member_payload(
        db: Session,
        member: CampaignMember,
    ) -> dict:
        user = (
            db.query(User)
            .filter(User.id == member.user_id)
            .first()
        )

        return {
            "id": member.id,
            "campaign_id": member.campaign_id,
            "user_id": member.user_id,
            "user_full_name": user.full_name if user else None,
            "user_email": user.email if user else None,
            "role": member.role,
            "status": member.status,
            "joined_at": member.joined_at,
        }

    @staticmethod
    def list_campaign_members(
        db: Session,
        campaign_id: str,
    ) -> list[dict]:
        members = (
            db.query(CampaignMember)
            .filter(CampaignMember.campaign_id == campaign_id)
            .filter(CampaignMember.status == CampaignMemberStatus.ACTIVE)
            .order_by(CampaignMember.joined_at.asc())
            .all()
        )

        return [
            OrganizationService._member_payload(
                db=db,
                member=member,
            )
            for member in members
        ]

    @staticmethod
    def remove_campaign_member(
        db: Session,
        current_user: User,
        campaign_id: str,
        user_id: str,
    ) -> None:
        campaign = OrganizationService._get_campaign(
            db=db,
            campaign_id=campaign_id,
        )

        if not campaign:
            raise ValueError("Campaign not found")

        if not OrganizationService._can_manage_campaign(db, current_user, campaign):
            raise PermissionError("You do not have permission to remove members")

        member = (
            db.query(CampaignMember)
            .filter(CampaignMember.campaign_id == campaign_id)
            .filter(CampaignMember.user_id == user_id)
            .first()
        )

        if not member:
            raise ValueError("Campaign member not found")

        member.status = CampaignMemberStatus.REMOVED
        db.commit()

    @staticmethod
    def add_challenge_to_campaign(
        db: Session,
        current_user: User,
        campaign_id: str,
        challenge_id: str,
    ) -> CampaignChallenge:
        campaign = OrganizationService._get_campaign(
            db=db,
            campaign_id=campaign_id,
        )

        if not campaign:
            raise ValueError("Campaign not found")

        if not OrganizationService._can_manage_campaign(db, current_user, campaign):
            raise PermissionError("You do not have permission to manage this campaign")

        challenge = (
            db.query(Challenge)
            .filter(Challenge.id == challenge_id)
            .first()
        )

        if not challenge:
            raise ValueError("Challenge not found")

        existing = (
            db.query(CampaignChallenge)
            .filter(CampaignChallenge.campaign_id == campaign_id)
            .filter(CampaignChallenge.challenge_id == challenge_id)
            .first()
        )

        if existing:
            existing.status = CampaignChallengeStatus.ACTIVE
            existing.added_by = current_user.id
            db.commit()
            db.refresh(existing)
            return existing

        link = CampaignChallenge(
            campaign_id=campaign_id,
            challenge_id=challenge_id,
            status=CampaignChallengeStatus.ACTIVE,
            added_by=current_user.id,
        )

        db.add(link)
        db.commit()
        db.refresh(link)

        return link

    @staticmethod
    def _campaign_challenge_payload(
        db: Session,
        link: CampaignChallenge,
    ) -> dict:
        challenge = (
            db.query(Challenge)
            .filter(Challenge.id == link.challenge_id)
            .first()
        )

        return {
            "id": link.id,
            "campaign_id": link.campaign_id,
            "challenge_id": link.challenge_id,
            "challenge_title": challenge.title if challenge else None,
            "category": challenge.category if challenge else None,
            "challenge_type": challenge.challenge_type if challenge else None,
            "difficulty": challenge.difficulty if challenge else None,
            "challenge_status": challenge.status if challenge else None,
            "status": link.status,
            "added_by": link.added_by,
            "added_at": link.added_at,
        }

    @staticmethod
    def list_campaign_challenges(
        db: Session,
        campaign_id: str,
    ) -> list[dict]:
        links = (
            db.query(CampaignChallenge)
            .filter(CampaignChallenge.campaign_id == campaign_id)
            .filter(CampaignChallenge.status == CampaignChallengeStatus.ACTIVE)
            .order_by(CampaignChallenge.added_at.desc())
            .all()
        )

        return [
            OrganizationService._campaign_challenge_payload(
                db=db,
                link=link,
            )
            for link in links
        ]

    @staticmethod
    def remove_challenge_from_campaign(
        db: Session,
        current_user: User,
        campaign_id: str,
        challenge_id: str,
    ) -> None:
        campaign = OrganizationService._get_campaign(
            db=db,
            campaign_id=campaign_id,
        )

        if not campaign:
            raise ValueError("Campaign not found")

        if not OrganizationService._can_manage_campaign(db, current_user, campaign):
            raise PermissionError("You do not have permission to manage this campaign")

        link = (
            db.query(CampaignChallenge)
            .filter(CampaignChallenge.campaign_id == campaign_id)
            .filter(CampaignChallenge.challenge_id == challenge_id)
            .first()
        )

        if not link:
            raise ValueError("Campaign challenge link not found")

        link.status = CampaignChallengeStatus.REMOVED
        db.commit()

    @staticmethod
    def _campaign_challenge_ids(
        db: Session,
        campaign_id: str,
    ) -> list[str]:
        rows = (
            db.query(CampaignChallenge.challenge_id)
            .filter(CampaignChallenge.campaign_id == campaign_id)
            .filter(CampaignChallenge.status == CampaignChallengeStatus.ACTIVE)
            .all()
        )

        return [
            row[0]
            for row in rows
        ]

    @staticmethod
    def get_campaign_dashboard(
        db: Session,
        campaign_id: str,
    ) -> dict:
        campaign = OrganizationService._get_campaign(
            db=db,
            campaign_id=campaign_id,
        )

        if not campaign:
            raise ValueError("Campaign not found")

        challenge_ids = OrganizationService._campaign_challenge_ids(
            db=db,
            campaign_id=campaign_id,
        )

        members_count = (
            db.query(CampaignMember)
            .filter(CampaignMember.campaign_id == campaign_id)
            .filter(CampaignMember.status == CampaignMemberStatus.ACTIVE)
            .count()
        )

        linked_challenges_count = len(challenge_ids)

        submissions_count = 0
        unique_participants_count = 0
        community_posts_count = 0
        total_co2e_saved_kg = 0.0
        total_trees_planted = 0.0
        total_biodiversity_score = 0.0

        if challenge_ids:
            submissions_count = (
                db.query(Submission)
                .filter(Submission.challenge_id.in_(challenge_ids))
                .count()
            )

            unique_participants_count = (
                db.query(Submission.user_id)
                .filter(Submission.challenge_id.in_(challenge_ids))
                .distinct()
                .count()
            )

            community_posts_count = (
                db.query(CommunityPost)
                .filter(CommunityPost.challenge_id.in_(challenge_ids))
                .count()
            )

            impact_totals = (
                db.query(
                    func.coalesce(func.sum(ImpactMetric.co2e_saved_kg), 0),
                    func.coalesce(func.sum(ImpactMetric.trees_planted), 0),
                    func.coalesce(func.sum(ImpactMetric.biodiversity_score), 0),
                )
                .filter(ImpactMetric.challenge_id.in_(challenge_ids))
                .first()
            )

            total_co2e_saved_kg = impact_totals[0] if impact_totals else 0.0
            total_trees_planted = impact_totals[1] if impact_totals else 0.0
            total_biodiversity_score = impact_totals[2] if impact_totals else 0.0

        return {
            "campaign_id": campaign.id,
            "campaign_title": campaign.title,
            "status": campaign.status,
            "members_count": members_count,
            "linked_challenges_count": linked_challenges_count,
            "submissions_count": submissions_count,
            "unique_participants_count": unique_participants_count,
            "community_posts_count": community_posts_count,
            "total_co2e_saved_kg": OrganizationService._round(total_co2e_saved_kg),
            "total_trees_planted": OrganizationService._round(total_trees_planted),
            "total_biodiversity_score": OrganizationService._round(
                total_biodiversity_score
            ),
            "target_participants": campaign.target_participants,
            "target_co2e_saved_kg": campaign.target_co2e_saved_kg,
            "target_trees_planted": campaign.target_trees_planted,
            "participant_progress_percent": OrganizationService._percent(
                unique_participants_count,
                campaign.target_participants,
            ),
            "co2e_progress_percent": OrganizationService._percent(
                total_co2e_saved_kg,
                campaign.target_co2e_saved_kg,
            ),
            "tree_progress_percent": OrganizationService._percent(
                total_trees_planted,
                campaign.target_trees_planted,
            ),
        }

    @staticmethod
    def get_organization_dashboard(
        db: Session,
        current_user: User,
    ) -> dict:
        organization = OrganizationService.get_my_profile(
            db=db,
            current_user=current_user,
        )

        campaigns = (
            db.query(Campaign)
            .filter(Campaign.organization_id == organization.id)
            .all()
        )

        campaign_ids = [
            campaign.id
            for campaign in campaigns
        ]

        campaigns_count = len(campaigns)

        active_campaigns_count = len(
            [
                campaign
                for campaign in campaigns
                if campaign.status == CampaignStatus.ACTIVE
            ]
        )

        members_count = 0
        linked_challenges_count = 0
        submissions_count = 0
        unique_participants_count = 0
        community_posts_count = 0
        total_co2e_saved_kg = 0.0
        total_trees_planted = 0.0
        total_biodiversity_score = 0.0

        if campaign_ids:
            members_count = (
                db.query(CampaignMember.user_id)
                .filter(CampaignMember.campaign_id.in_(campaign_ids))
                .filter(CampaignMember.status == CampaignMemberStatus.ACTIVE)
                .distinct()
                .count()
            )

            challenge_rows = (
                db.query(CampaignChallenge.challenge_id)
                .filter(CampaignChallenge.campaign_id.in_(campaign_ids))
                .filter(CampaignChallenge.status == CampaignChallengeStatus.ACTIVE)
                .distinct()
                .all()
            )

            challenge_ids = [
                row[0]
                for row in challenge_rows
            ]

            linked_challenges_count = len(challenge_ids)

            if challenge_ids:
                submissions_count = (
                    db.query(Submission)
                    .filter(Submission.challenge_id.in_(challenge_ids))
                    .count()
                )

                unique_participants_count = (
                    db.query(Submission.user_id)
                    .filter(Submission.challenge_id.in_(challenge_ids))
                    .distinct()
                    .count()
                )

                community_posts_count = (
                    db.query(CommunityPost)
                    .filter(CommunityPost.challenge_id.in_(challenge_ids))
                    .count()
                )

                impact_totals = (
                    db.query(
                        func.coalesce(func.sum(ImpactMetric.co2e_saved_kg), 0),
                        func.coalesce(func.sum(ImpactMetric.trees_planted), 0),
                        func.coalesce(func.sum(ImpactMetric.biodiversity_score), 0),
                    )
                    .filter(ImpactMetric.challenge_id.in_(challenge_ids))
                    .first()
                )

                total_co2e_saved_kg = impact_totals[0] if impact_totals else 0.0
                total_trees_planted = impact_totals[1] if impact_totals else 0.0
                total_biodiversity_score = impact_totals[2] if impact_totals else 0.0

        return {
            "organization_id": organization.id,
            "organization_name": organization.organization_name,
            "campaigns_count": campaigns_count,
            "active_campaigns_count": active_campaigns_count,
            "members_count": members_count,
            "linked_challenges_count": linked_challenges_count,
            "submissions_count": submissions_count,
            "unique_participants_count": unique_participants_count,
            "community_posts_count": community_posts_count,
            "total_co2e_saved_kg": OrganizationService._round(total_co2e_saved_kg),
            "total_trees_planted": OrganizationService._round(total_trees_planted),
            "total_biodiversity_score": OrganizationService._round(
                total_biodiversity_score
            ),
        }