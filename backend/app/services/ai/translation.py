from app.schemas.common import Article


class VernacularEngine:
    def translate_feature(self, article: Article) -> dict[str, str]:
        base = article.summary
        return {
            "Hindi": f"{base} निवेशकों के लिए इसका मतलब है कि पूंजी आवंटन और नीति संकेत दोनों पर नज़र रखें।",
            "Tamil": f"{base} முதலீட்டாளர்கள் மூலதன ஒதுக்கீடும் கொள்கை மாற்றங்களும் எப்படி இணைகிறது என்பதை கவனிக்க வேண்டும்.",
            "Telugu": f"{base} పెట్టుబడిదారులు మూలధన వ్యయం, విధాన సంకేతాలు, మరియు మార్కెట్ భావోద్వేగాన్ని కలిసి చూడాలి.",
            "Bengali": f"{base} বিনিয়োগকারীদের জন্য মূল বিষয় হলো পুঁজি ব্যয়, নীতিগত ইঙ্গিত এবং বাজারের মনোভাব একসঙ্গে বোঝা।",
        }
