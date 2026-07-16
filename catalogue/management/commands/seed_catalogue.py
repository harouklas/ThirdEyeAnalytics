"""Command that creates sample ThirdEye categories, sub-categories, and services."""

from decimal import Decimal

from django.core.management.base import BaseCommand

from catalogue.models import Category, Service, SubCategory


class Command(BaseCommand):
    help = "Add sample ThirdEye categories, sub-categories, and services."

    def handle(self, *args, **options):
        # Keep each category together with the sub-categories that belong to it.
        categories = [
            {
                "name": "Match Analysis",
                "slug": "match-analysis",
                "description": "Services that help coaches understand team tactics and match events.",
                "subcategories": [
                    ("Tactical Reports", "tactical-reports"),
                    ("Team Shape Analysis", "team-shape-analysis"),
                    ("Possession Analysis", "possession-analysis"),
                    ("Pressing Analysis", "pressing-analysis"),
                ],
            },
            {
                "name": "Player Analysis",
                "slug": "player-analysis",
                "description": "Services focused on individual player movement and performance.",
                "subcategories": [
                    ("Player Tracking", "player-tracking"),
                    ("Heatmaps", "heatmaps"),
                    ("Speed & Distance", "speed-distance"),
                    ("Individual Reports", "individual-reports"),
                ],
            },
            {
                "name": "Scouting Tools",
                "slug": "scouting-tools",
                "description": "Services for scouts, academies, and recruitment teams.",
                "subcategories": [
                    ("Talent Reports", "talent-reports"),
                    ("Video Review", "video-review"),
                    ("Player Comparison", "player-comparison"),
                    ("Highlight Detection", "highlight-detection"),
                ],
            },
            {
                "name": "Video Processing",
                "slug": "video-processing",
                "description": "Computer vision services that prepare football video for analysis.",
                "subcategories": [
                    ("Pitch Detection", "pitch-detection"),
                    ("Camera Calibration", "camera-calibration"),
                    ("Object Detection", "object-detection"),
                    ("Video Enhancement", "video-enhancement"),
                ],
            },
        ]

        # update_or_create lets us run this command again without creating duplicates.
        for category_data in categories:
            category, _created = Category.objects.update_or_create(
                slug=category_data["slug"],
                defaults={
                    "name": category_data["name"],
                    "description": category_data["description"],
                },
            )

            for subcategory_name, subcategory_slug in category_data["subcategories"]:
                SubCategory.objects.update_or_create(
                    category=category,
                    slug=subcategory_slug,
                    defaults={"name": subcategory_name},
                )

        # These sample services give the catalogue useful data for the demonstration.
        service_data = [
            {
                "name": "Full Match Tactical Report",
                "slug": "full-match-tactical-report",
                "category": "match-analysis",
                "subcategory": "tactical-reports",
                "short_description": "A coach-friendly report explaining the main tactical patterns in a full match.",
                "description": "ThirdEye reviews a full football match and prepares a tactical report covering formations, attacking patterns, defensive problems, and key moments.",
                "analysis_type": Service.AnalysisType.TACTICAL,
                "skill_level": Service.SkillLevel.PROFESSIONAL,
                "video_type": Service.VideoType.FULL_MATCH,
                "delivery_time": Service.DeliveryTime.DAYS_3_5,
                "output_format": Service.OutputFormat.PDF_REPORT,
                "price": Decimal("149.00"),
                "is_featured": True,
            },
            {
                "name": "Team Shape Detection",
                "slug": "team-shape-detection",
                "category": "match-analysis",
                "subcategory": "team-shape-analysis",
                "short_description": "Detects how a team keeps its shape during attacking and defending phases.",
                "description": "This service studies team positioning and explains how compact or stretched the team becomes during different match phases.",
                "analysis_type": Service.AnalysisType.TEAM_SHAPE,
                "skill_level": Service.SkillLevel.SEMI_PRO,
                "video_type": Service.VideoType.FULL_MATCH,
                "delivery_time": Service.DeliveryTime.HOURS_48,
                "output_format": Service.OutputFormat.DASHBOARD,
                "price": Decimal("119.00"),
                "is_featured": True,
            },
            {
                "name": "Pressing Intensity Report",
                "slug": "pressing-intensity-report",
                "category": "match-analysis",
                "subcategory": "pressing-analysis",
                "short_description": "Shows where and when the team applies pressure on the opponent.",
                "description": "The report highlights pressing zones, pressing triggers, and moments where the opponent escaped pressure.",
                "analysis_type": Service.AnalysisType.TACTICAL,
                "skill_level": Service.SkillLevel.ACADEMY,
                "video_type": Service.VideoType.FULL_MATCH,
                "delivery_time": Service.DeliveryTime.HOURS_48,
                "output_format": Service.OutputFormat.PDF_REPORT,
                "price": Decimal("89.00"),
                "is_featured": False,
            },
            {
                "name": "Player Tracking Package",
                "slug": "player-tracking-package",
                "category": "player-analysis",
                "subcategory": "player-tracking",
                "short_description": "Tracks a selected player's movement across the match video.",
                "description": "ThirdEye follows one selected player and provides movement patterns, positioning notes, and key actions.",
                "analysis_type": Service.AnalysisType.TRACKING,
                "skill_level": Service.SkillLevel.ACADEMY,
                "video_type": Service.VideoType.PLAYER_CLIPS,
                "delivery_time": Service.DeliveryTime.HOURS_48,
                "output_format": Service.OutputFormat.VIDEO_OVERLAY,
                "price": Decimal("79.00"),
                "is_featured": True,
            },
            {
                "name": "Player Heatmap Generation",
                "slug": "player-heatmap-generation",
                "category": "player-analysis",
                "subcategory": "heatmaps",
                "short_description": "Creates a visual heatmap showing where a player was most active.",
                "description": "This service turns player movement into an easy-to-read heatmap for coaches, players, and analysts.",
                "analysis_type": Service.AnalysisType.HEATMAP,
                "skill_level": Service.SkillLevel.AMATEUR,
                "video_type": Service.VideoType.PLAYER_CLIPS,
                "delivery_time": Service.DeliveryTime.HOURS_24,
                "output_format": Service.OutputFormat.PDF_REPORT,
                "price": Decimal("49.00"),
                "is_featured": False,
            },
            {
                "name": "Sprint & Distance Report",
                "slug": "sprint-distance-report",
                "category": "player-analysis",
                "subcategory": "speed-distance",
                "short_description": "Summarizes player speed, sprint actions, and covered distance.",
                "description": "The report estimates movement intensity from video and gives a simple performance summary for one player.",
                "analysis_type": Service.AnalysisType.PERFORMANCE,
                "skill_level": Service.SkillLevel.SEMI_PRO,
                "video_type": Service.VideoType.FULL_MATCH,
                "delivery_time": Service.DeliveryTime.DAYS_3_5,
                "output_format": Service.OutputFormat.CSV_DATA,
                "price": Decimal("99.00"),
                "is_featured": False,
            },
            {
                "name": "AI Scouting Report",
                "slug": "ai-scouting-report",
                "category": "scouting-tools",
                "subcategory": "talent-reports",
                "short_description": "A scouting-style report for evaluating a player from video clips.",
                "description": "ThirdEye reviews player clips and creates a structured report with strengths, weaknesses, and recommendation notes.",
                "analysis_type": Service.AnalysisType.SCOUTING,
                "skill_level": Service.SkillLevel.PROFESSIONAL,
                "video_type": Service.VideoType.PLAYER_CLIPS,
                "delivery_time": Service.DeliveryTime.DAYS_3_5,
                "output_format": Service.OutputFormat.PDF_REPORT,
                "price": Decimal("129.00"),
                "is_featured": True,
            },
            {
                "name": "Player Comparison Analysis",
                "slug": "player-comparison-analysis",
                "category": "scouting-tools",
                "subcategory": "player-comparison",
                "short_description": "Compares two players using the same simple football criteria.",
                "description": "The comparison includes movement, involvement, decision-making, and performance notes from available video.",
                "analysis_type": Service.AnalysisType.SCOUTING,
                "skill_level": Service.SkillLevel.SEMI_PRO,
                "video_type": Service.VideoType.PLAYER_CLIPS,
                "delivery_time": Service.DeliveryTime.DAYS_3_5,
                "output_format": Service.OutputFormat.PDF_REPORT,
                "price": Decimal("139.00"),
                "is_featured": False,
            },
            {
                "name": "Automatic Highlight Detection",
                "slug": "automatic-highlight-detection",
                "category": "scouting-tools",
                "subcategory": "highlight-detection",
                "short_description": "Finds important actions and creates a highlight-style summary.",
                "description": "This service detects key video moments such as shots, runs, tackles, and attacking actions.",
                "analysis_type": Service.AnalysisType.HIGHLIGHT,
                "skill_level": Service.SkillLevel.ACADEMY,
                "video_type": Service.VideoType.FULL_MATCH,
                "delivery_time": Service.DeliveryTime.HOURS_48,
                "output_format": Service.OutputFormat.VIDEO_OVERLAY,
                "price": Decimal("109.00"),
                "is_featured": True,
            },
            {
                "name": "Automatic Pitch Detection",
                "slug": "automatic-pitch-detection",
                "category": "video-processing",
                "subcategory": "pitch-detection",
                "short_description": "Detects the pitch area so match footage can be prepared for analysis.",
                "description": "ThirdEye identifies the visible pitch area and prepares the video for further computer vision processing.",
                "analysis_type": Service.AnalysisType.DETECTION,
                "skill_level": Service.SkillLevel.PROFESSIONAL,
                "video_type": Service.VideoType.FULL_MATCH,
                "delivery_time": Service.DeliveryTime.HOURS_24,
                "output_format": Service.OutputFormat.CSV_DATA,
                "price": Decimal("69.00"),
                "is_featured": False,
            },
            {
                "name": "Camera Angle Calibration",
                "slug": "camera-angle-calibration",
                "category": "video-processing",
                "subcategory": "camera-calibration",
                "short_description": "Improves video geometry before tactical or tracking analysis.",
                "description": "This service prepares camera footage by estimating the camera angle and improving the consistency of visual analysis.",
                "analysis_type": Service.AnalysisType.DETECTION,
                "skill_level": Service.SkillLevel.PROFESSIONAL,
                "video_type": Service.VideoType.FULL_MATCH,
                "delivery_time": Service.DeliveryTime.HOURS_48,
                "output_format": Service.OutputFormat.CSV_DATA,
                "price": Decimal("89.00"),
                "is_featured": False,
            },
            {
                "name": "Ball Detection Service",
                "slug": "ball-detection-service",
                "category": "video-processing",
                "subcategory": "object-detection",
                "short_description": "Detects ball movement in football match or training footage.",
                "description": "The service locates the ball in video frames and prepares a simple tracking output for analysis.",
                "analysis_type": Service.AnalysisType.DETECTION,
                "skill_level": Service.SkillLevel.SEMI_PRO,
                "video_type": Service.VideoType.TRAINING,
                "delivery_time": Service.DeliveryTime.HOURS_48,
                "output_format": Service.OutputFormat.VIDEO_OVERLAY,
                "price": Decimal("99.00"),
                "is_featured": False,
            },
        ]

        # Look up each service's category records before saving the service itself.
        for item in service_data:
            category = Category.objects.get(slug=item["category"])
            subcategory = SubCategory.objects.get(
                category=category,
                slug=item["subcategory"],
            )

            Service.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "category": category,
                    "subcategory": subcategory,
                    "name": item["name"],
                    "short_description": item["short_description"],
                    "description": item["description"],
                    "analysis_type": item["analysis_type"],
                    "skill_level": item["skill_level"],
                    "video_type": item["video_type"],
                    "delivery_time": item["delivery_time"],
                    "output_format": item["output_format"],
                    "price": item["price"],
                    "is_featured": item["is_featured"],
                    "is_active": True,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "ThirdEye sample catalogue created: "
                f"{Category.objects.count()} categories, "
                f"{SubCategory.objects.count()} sub-categories, "
                f"{Service.objects.count()} services."
            )
        )
