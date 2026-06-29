from app.ai.languages import normalize_language


class LocalizedResponseService:
    @staticmethod
    def detect_topic(
        message: str,
    ) -> str:
        text = message.lower()

        if any(
            word in text
            for word in [
                "plastic",
                "single-use",
                "single use",
                "bottle",
                "bag",
                "waste",
            ]
        ):
            return "plastic"

        if any(
            word in text
            for word in [
                "water",
                "save water",
                "conserve water",
                "tap",
                "leak",
            ]
        ):
            return "water"

        if any(
            word in text
            for word in [
                "tree",
                "plant",
                "sapling",
                "plantation",
            ]
        ):
            return "tree"

        if any(
            word in text
            for word in [
                "recycle",
                "recycling",
                "dry waste",
                "wet waste",
            ]
        ):
            return "recycling"

        return "general"

    @staticmethod
    def get_chat_answer(
        message: str,
        language: str,
    ) -> str | None:
        language = normalize_language(language)
        topic = LocalizedResponseService.detect_topic(
            message=message,
        )

        templates = {
            "plastic": {
                "en": (
                    "To reduce plastic waste:\n"
                    "1. Use a cloth bag instead of plastic bags.\n"
                    "2. Carry a reusable water bottle.\n"
                    "3. Avoid single-use plastic cups, plates, and straws.\n"
                    "4. Separate dry waste and give plastic for recycling.\n"
                    "5. Reuse containers whenever possible."
                ),
                "kn": (
                    "ಪ್ಲಾಸ್ಟಿಕ್ ತ್ಯಾಜ್ಯವನ್ನು ಕಡಿಮೆ ಮಾಡಲು:\n"
                    "1. ಪ್ಲಾಸ್ಟಿಕ್ ಚೀಲದ ಬದಲು ಬಟ್ಟೆ ಚೀಲ ಬಳಸಿ.\n"
                    "2. ಒಂದೇ ಬಾರಿ ಬಳಸುವ ಪ್ಲಾಸ್ಟಿಕ್ ಬಾಟಲ್‌ಗಳನ್ನು ತಪ್ಪಿಸಿ.\n"
                    "3. ನಿಮ್ಮದೇ ನೀರಿನ ಬಾಟಲ್ ತೆಗೆದುಕೊಂಡು ಹೋಗಿ.\n"
                    "4. ಒಣ ಕಸ ಮತ್ತು ತೇವ ಕಸವನ್ನು ಬೇರ್ಪಡಿಸಿ.\n"
                    "5. ಸಾಧ್ಯವಾದರೆ ಪ್ಲಾಸ್ಟಿಕ್ ವಸ್ತುಗಳನ್ನು ಮರುಬಳಕೆ ಮಾಡಿ."
                ),
                "hi": (
                    "प्लास्टिक कचरा कम करने के लिए:\n"
                    "1. प्लास्टिक बैग की जगह कपड़े का बैग इस्तेमाल करें।\n"
                    "2. अपनी reusable पानी की बोतल साथ रखें।\n"
                    "3. single-use plastic cups, plates और straws से बचें।\n"
                    "4. गीले और सूखे कचरे को अलग रखें।\n"
                    "5. प्लास्टिक वस्तुओं को recycle या reuse करें।"
                ),
                "ta": (
                    "பிளாஸ்டிக் கழிவை குறைக்க:\n"
                    "1. பிளாஸ்டிக் பையின் பதிலாக துணி பையை பயன்படுத்துங்கள்.\n"
                    "2. உங்கள் சொந்த தண்ணீர் பாட்டிலை எடுத்துச் செல்லுங்கள்.\n"
                    "3. ஒருமுறை பயன்படுத்தும் பிளாஸ்டிக் பொருட்களை தவிர்க்குங்கள்.\n"
                    "4. ஈரக் குப்பை மற்றும் உலர் குப்பையை தனியாக பிரிக்குங்கள்.\n"
                    "5. முடிந்தவரை பிளாஸ்டிக் பொருட்களை மறுபயன்பாடு செய்யுங்கள்."
                ),
                "te": (
                    "ప్లాస్టిక్ వ్యర్థాలను తగ్గించడానికి:\n"
                    "1. ప్లాస్టిక్ బ్యాగ్ బదులు గుడ్డ సంచి వాడండి.\n"
                    "2. మీ reusable నీటి బాటిల్ వెంట తీసుకెళ్లండి.\n"
                    "3. ఒక్కసారి వాడే ప్లాస్టిక్ కప్పులు, ప్లేట్లు, స్ట్రాలు వాడకండి.\n"
                    "4. తడి చెత్త మరియు పొడి చెత్తను వేరు చేయండి.\n"
                    "5. సాధ్యమైనంత వరకు ప్లాస్టిక్ వస్తువులను మళ్లీ వాడండి."
                ),
            },
            "water": {
                "en": (
                    "To save water:\n"
                    "1. Turn off the tap while brushing.\n"
                    "2. Fix leaking taps quickly.\n"
                    "3. Use a bucket instead of a long shower.\n"
                    "4. Reuse water for plants when possible.\n"
                    "5. Avoid wasting water while washing vehicles."
                ),
                "kn": (
                    "ನೀರನ್ನು ಉಳಿಸಲು:\n"
                    "1. ಹಲ್ಲು ತೊಳೆಯುವಾಗ ಟ್ಯಾಪ್ ಮುಚ್ಚಿ.\n"
                    "2. ನೀರು ಸೋರಿಕೆಯಾದರೆ ಬೇಗ ಸರಿಪಡಿಸಿ.\n"
                    "3. ದೀರ್ಘ ಶವರ್ ಬದಲು ಬಕೆಟ್ ಬಳಸಿ.\n"
                    "4. ಸಾಧ್ಯವಾದರೆ ಉಳಿದ ನೀರನ್ನು ಗಿಡಗಳಿಗೆ ಬಳಸಿ.\n"
                    "5. ವಾಹನ ತೊಳೆಯುವಾಗ ನೀರನ್ನು ವ್ಯರ್ಥ ಮಾಡಬೇಡಿ."
                ),
                "hi": (
                    "पानी बचाने के लिए:\n"
                    "1. ब्रश करते समय नल बंद रखें।\n"
                    "2. leaking taps को जल्दी ठीक करें।\n"
                    "3. लंबे shower की जगह bucket का उपयोग करें।\n"
                    "4. बचा हुआ पानी पौधों के लिए उपयोग करें।\n"
                    "5. वाहन धोते समय पानी बर्बाद न करें।"
                ),
                "ta": (
                    "தண்ணீரை சேமிக்க:\n"
                    "1. பல் துலக்கும் போது குழாயை மூடுங்கள்.\n"
                    "2. கசிவு உள்ள குழாய்களை உடனே சரி செய்யுங்கள்.\n"
                    "3. நீண்ட shower பதிலாக bucket பயன்படுத்துங்கள்.\n"
                    "4. மீதமுள்ள தண்ணீரை செடிகளுக்கு பயன்படுத்துங்கள்.\n"
                    "5. வாகனம் கழுவும் போது தண்ணீரை வீணாக்க வேண்டாம்."
                ),
                "te": (
                    "నీటిని ఆదా చేయడానికి:\n"
                    "1. పళ్ళు తోమేటప్పుడు ట్యాప్ మూసివేయండి.\n"
                    "2. నీరు లీక్ అయితే వెంటనే సరి చేయండి.\n"
                    "3. ఎక్కువసేపు shower బదులు bucket వాడండి.\n"
                    "4. మిగిలిన నీటిని మొక్కలకు వాడండి.\n"
                    "5. వాహనం కడిగేటప్పుడు నీటిని వృథా చేయవద్దు."
                ),
            },
            "general": {
                "en": (
                    "You can live more eco-friendly by:\n"
                    "1. Reducing plastic use.\n"
                    "2. Saving water and electricity.\n"
                    "3. Planting and caring for trees.\n"
                    "4. Separating wet and dry waste.\n"
                    "5. Using public transport or walking for short distances."
                ),
                "kn": (
                    "ಪರಿಸರ ಸ್ನೇಹಿ ಜೀವನಕ್ಕಾಗಿ:\n"
                    "1. ಪ್ಲಾಸ್ಟಿಕ್ ಬಳಕೆಯನ್ನು ಕಡಿಮೆ ಮಾಡಿ.\n"
                    "2. ನೀರು ಮತ್ತು ವಿದ್ಯುತ್ ಉಳಿಸಿ.\n"
                    "3. ಗಿಡಗಳನ್ನು ನೆಟ್ಟು ಆರೈಕೆ ಮಾಡಿ.\n"
                    "4. ಒಣ ಕಸ ಮತ್ತು ತೇವ ಕಸವನ್ನು ಬೇರ್ಪಡಿಸಿ.\n"
                    "5. ಹತ್ತಿರದ ಸ್ಥಳಗಳಿಗೆ ನಡೆದು ಹೋಗಿ ಅಥವಾ ಸಾರ್ವಜನಿಕ ಸಾರಿಗೆ ಬಳಸಿ."
                ),
                "hi": (
                    "पर्यावरण के अनुकूल जीवन के लिए:\n"
                    "1. प्लास्टिक का उपयोग कम करें।\n"
                    "2. पानी और बिजली बचाएं।\n"
                    "3. पेड़ लगाएं और उनकी देखभाल करें।\n"
                    "4. गीले और सूखे कचरे को अलग करें।\n"
                    "5. छोटी दूरी के लिए पैदल चलें या public transport इस्तेमाल करें।"
                ),
                "ta": (
                    "சுற்றுச்சூழல் நட்பு வாழ்க்கைக்காக:\n"
                    "1. பிளாஸ்டிக் பயன்பாட்டை குறைக்குங்கள்.\n"
                    "2. தண்ணீர் மற்றும் மின்சாரத்தை சேமிக்குங்கள்.\n"
                    "3. மரம் நட்டு பராமரிக்குங்கள்.\n"
                    "4. ஈரக் குப்பை மற்றும் உலர் குப்பையை பிரிக்குங்கள்.\n"
                    "5. அருகிலுள்ள இடங்களுக்கு நடந்து செல்லுங்கள் அல்லது public transport பயன்படுத்துங்கள்."
                ),
                "te": (
                    "పర్యావరణానికి అనుకూలంగా జీవించడానికి:\n"
                    "1. ప్లాస్టిక్ వాడకాన్ని తగ్గించండి.\n"
                    "2. నీరు మరియు విద్యుత్ ఆదా చేయండి.\n"
                    "3. చెట్లు నాటి వాటిని సంరక్షించండి.\n"
                    "4. తడి చెత్త మరియు పొడి చెత్తను వేరు చేయండి.\n"
                    "5. దగ్గర ప్రాంతాలకు నడిచి వెళ్లండి లేదా public transport వాడండి."
                ),
            },
        }

        topic_templates = templates.get(
            topic,
            templates["general"],
        )

        return topic_templates.get(language)