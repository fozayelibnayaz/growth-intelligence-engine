"""
Eagle 3D Intelligence Platform - Auto Content Outline Generator
Expanded content types based on user requirements.
"""

from datetime import datetime
import random

class ContentOutlineGenerator:
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """Load content templates for various content types"""
        return {
            'Blog Post': {
                'structure': [
                    'Introduction & Hook', 'Problem/Topic Deep Dive', 
                    'Eagle 3D Solution', 'Step-by-Step Guide/Best Practices', 
                    'Advanced Tips/Troubleshooting', 'Conclusion & CTA'
                ],
                'word_count': '1500-2500 words',
                'time_estimate': '2-3 days',
                'platforms': ['Website Blog', 'Medium', 'LinkedIn Article'],
                'format': 'Text with images'
            },
            'YouTube Video': {
                'structure': [
                    'Intro Hook (0:00-0:15)', 'Problem/Topic Overview (0:15-1:00)', 
                    'Eagle 3D Demo/Explanation (1:00-3:00)', 'Walkthrough/Tutorial (3:00-8:00)', 
                    'Q&A/Tips (8:00-9:00)', 'Outro & CTA (9:00-10:00)'
                ],
                'word_count': 'Script: 1500-2000 words (10-15 min video)',
                'time_estimate': '3-5 days',
                'platforms': ['YouTube'],
                'format': 'Video with screen recording/demos'
            },
            'YouTube Short': {
                'structure': [
                    'Problem/Tip (0:00-0:05)', 'Quick Solution/Benefit (0:05-0:15)', 
                    'Eagle 3D Mention (0:15-0:20)', 'CTA (0:20-0:30)'
                ],
                'word_count': 'Script: 50-100 words (30 sec video)',
                'time_estimate': '0.5-1 day',
                'platforms': ['YouTube Shorts', 'Instagram Reels', 'TikTok'],
                'format': 'Short vertical video'
            },
            'Newsletter': {
                'structure': [
                    'Catchy Subject Line', 'Personalized Greeting', 
                    'Brief Problem/Insight', 'Link to Full Blog/Video', 
                    'Eagle 3D Feature Highlight', 'Quick Tip/Value-add', 'CTA'
                ],
                'word_count': '300-500 words',
                'time_estimate': '1 day',
                'platforms': ['Email Marketing Platform', 'LinkedIn Newsletter'],
                'format': 'Email/Text'
            },
            'Social Media Post': {
                'structure': [
                    'Hook/Question', 'Key Takeaway/Solution', 
                    'Relevant Hashtags', 'Link to Resource', 'Call for Engagement'
                ],
                'word_count': '50-150 words',
                'time_estimate': '0.5 day',
                'platforms': ['LinkedIn', 'Twitter/X', 'Facebook', 'Discord'],
                'format': 'Short text with image/GIF'
            },
            'Workshop/Webinar': {
                'structure': [
                    'Title & Learning Objectives', 'Agenda (3-5 key topics)', 
                    'Live Demo Sections', 'Q&A Session', 'Eagle 3D Integration', 'Resources & CTA'
                ],
                'word_count': 'Presentation Script: 3000-5000 words (60-90 min session)',
                'time_estimate': '5-10 days',
                'platforms': ['Zoom', 'Google Meet', 'Eventbrite'],
                'format': 'Live presentation with slides & demo'
            },
            'Podcast Episode': {
                'structure': [
                    'Intro Music & Host Welcome', 'Topic Introduction', 
                    'Interview/Discussion (key points)', 'Eagle 3D Relevance', 
                    'Tips/Insights', 'Audience Q&A', 'Outro & CTA'
                ],
                'word_count': 'Script: 2000-3000 words (30-45 min episode)',
                'time_estimate': '3-5 days',
                'platforms': ['Spotify', 'Apple Podcasts', 'Google Podcasts'],
                'format': 'Audio recording'
            },
            'Spotlight Video/Article': {
                'structure': [
                    'Hero Shot/Headline', 'Client/Use Case Introduction', 
                    'Challenge', 'Eagle 3D Solution', 'Results & Metrics', 
                    'Testimonial/Quote', 'Future Outlook & CTA'
                ],
                'word_count': '750-1500 words (Article) / 500-1000 words (Video Script)',
                'time_estimate': '2-4 days',
                'platforms': ['Website Case Study', 'YouTube', 'LinkedIn Article'],
                'format': 'Story-driven text/video'
            }
        }
    
    def generate_outline(self, keyword, category, content_type=None, is_b2b=False):
        """Generate complete content outline"""
        # Select content type based on category, B2B, and general preference
        if content_type is None:
            if is_b2b:
                content_type = random.choice(['Case Study', 'Workshop/Webinar', 'Spotlight Video/Article', 'LinkedIn Article'])
            elif "tutorial" in category.lower() or "guide" in category.lower():
                content_type = random.choice(['Blog Post', 'YouTube Video', 'Newsletter'])
            else:
                content_type = random.choice(['Blog Post', 'YouTube Short', 'Social Media Post'])
        
        template = self.templates.get(content_type, self.templates['Blog Post'])
        
        # SEO Keywords
        seo_keywords = [
            keyword,
            'pixel streaming',
            'Unreal Engine',
            'WebRTC',
            'cloud gaming',
            'Eagle 3D Streaming'
        ]
        
        # Generate title variations
        titles = [
            f"{content_type}: How to Fix {keyword} in Unreal Engine (2026 Guide)",
            f"{content_type}: Mastering {keyword} for Optimal Pixel Streaming Performance",
            f"{content_type}: {category.replace('_', ' ').title()} with Eagle 3D Streaming",
            f"{content_type}: Avoiding {keyword} Pitfalls in Your Unreal Projects",
            f"{content_type}: The Complete {keyword} [Solution/Tutorial] for {template.get('target_audience', 'Developers')}"
        ]
        
        # Generate outline
        outline_str = f"""
📝 COMPLETE CONTENT OUTLINE
═══════════════════════════════════════════════════════════════

🎯 **PRIMARY KEYWORD:** {keyword}
📂 **CATEGORY:** {category.replace('_', ' ').title()}
📝 **RECOMMENDED CONTENT TYPE:** {content_type}
💼 **B2B FOCUSED:** {'Yes' if is_b2b else 'No'}

═══════════════════════════════════════════════════════════════
📌 **TITLE OPTIONS (Pick 1, customize for platform)**
═══════════════════════════════════════════════════════════════
"""
        for i, title in enumerate(titles, 1):
            outline_str += f"{i}. {title}\n"
        
        outline_str += f"""
═══════════════════════════════════════════════════════════════
📋 **CONTENT STRUCTURE ({template['format']} - {content_type})**
═══════════════════════════════════════════════════════════════
"""
        for i, section in enumerate(template['structure'], 1):
            outline_str += f"{i}. {section}\n"
            outline_str += f"   - [Key points for this section]\n"
            outline_str += f"   - [Include relevant examples/screenshots/demos]\n\n"
        
        outline_str += f"""
═══════════════════════════════════════════════════════════════
🎯 **SEO KEYWORDS**
═══════════════════════════════════════════════════════════════
Primary: {', '.join(seo_keywords[:3])}
Secondary: {', '.join(seo_keywords[3:])}
Long-tail: {keyword} tutorial, {keyword} fix, {keyword} guide, Eagle 3D {keyword}

═══════════════════════════════════════════════════════════════
📱 **PLATFORM DISTRIBUTION**
═══════════════════════════════════════════════════════════════
"""
        for platform in template['platforms']:
            outline_str += f"• {platform}\n"
        
        outline_str += f"""
═══════════════════════════════════════════════════════════════
⏱️ **PRODUCTION DETAILS**
═══════════════════════════════════════════════════════════════
Word Count: {template['word_count']}
Time Estimate: {template['time_estimate']}
Difficulty: {'Advanced' if is_b2b else 'Beginner-Friendly'}

═══════════════════════════════════════════════════════════════
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════
"""
        
        return {
            'full_outline': outline_str,
            'titles': titles,
            'seo_keywords': seo_keywords,
            'platforms': template['platforms'],
            'time_estimate': template['time_estimate'],
            'word_count': template['word_count']
        }