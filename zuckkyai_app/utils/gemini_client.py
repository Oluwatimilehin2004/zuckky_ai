import google.generativeai as genai
from django.conf import settings

class GeminiClient:
    def __init__(self):
        self.model = None
        
        # Latest Gemini models (November 2024)
        self.available_models = [
            'gemini-2.0-flash',  # Latest fast model
            'gemini-2.0-flash-exp',  # Experimental version
            'gemini-1.5-flash',  # Previous fast model
            'gemini-1.5-pro',    # Previous pro model
            'gemini-pro',        # Legacy model
            'models/gemini-pro', # Some API versions
        ]
        
        print("🚀 Initializing Gemini client with latest models...")
        
        for model_name in self.available_models:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ SUCCESS! Initialized with model: {model_name}")
                break
            except Exception as e:
                print(f"❌ Failed with {model_name}: {e}")
                continue
        
        if not self.model:
            print("⚠️ No Gemini models available - using fallback mode")
        else:
            print("🎉 Gemini AI is ready to help with video editing!")
        
    def get_chat_response(self, user_message, conversation_history=None):
        """Get AI response from Gemini"""
        try:
            if not self.model:
                return self._get_fallback_response(user_message)
            
            # Create context for video editing
            context = """You are Zuckky AI, an enthusiastic video editing assistant. You help users create viral videos.

Your personality:
- Energetic and creative 🎬
- Focused on video editing and content creation
- Helpful with uploads, templates, and AI processing
- Use emojis occasionally to be engaging

Keep responses concise and focused on video editing. Guide users through the process."""

            # Build conversation
            prompt = f"{context}\n\nUser: {user_message}\n\nZuckky AI:"
            
            print(f"💬 Sending to Gemini: {user_message}")
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                print(f"🤖 Gemini response: {response.text}")
                return response.text
            else:
                return self._get_fallback_response(user_message)
            
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, user_message):
        """Provide engaging fallback responses"""
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ['hello', 'hi', 'hey']):
            return "Hey there! I'm Zuckky AI, your video editing assistant! 🎬 Ready to create some amazing viral content? Just upload your footage and let's get started! 🚀"
        
        elif any(word in user_message_lower for word in ['upload', 'video', 'footage']):
            return "Perfect! 🎥 To begin, please upload your raw video. You can click the upload area or drag & drop your file. I support MP4, MOV, AVI - up to 2GB! Then we'll choose an awesome editing style! ✨"
        
        elif any(word in user_message_lower for word in ['template', 'style', 'viral']):
            return "We've got some killer templates! 🔥 Choose from:\n\n⚡ **Alex Hormozi** - Fast cuts, bold text, high energy\n🎯 **Iman Gadzhi** - Cinematic, smooth B-roll\n🎭 **Gary Vee** - Authentic, raw, engaging\n✨ **Custom Style** - Upload a reference video to train AI\n\nWhich style speaks to you? 😎"
        
        elif any(word in user_message_lower for word in ['edit', 'process', 'continue']):
            return "I'm ready to work my AI magic! ✨ But first, I need your video footage. Upload your raw video and we'll transform it into viral-ready content together! 🎉"
        
        elif any(word in user_message_lower for word in ['help', 'how', 'what']):
            return "I've got you! Here's the simple process:\n\n1️⃣ **Upload** your raw video footage\n2️⃣ **Choose** a viral template style\n3️⃣ **Add** any special instructions\n4️⃣ **Watch** as AI creates your professional edit!\n\nYou've got 32 credits ready to use! 💪 What would you like to start with?"
        
        elif any(word in user_message_lower for word in ['credit', 'price', 'cost']):
            return "You're rocking 32 editing credits! 🎉 Each video edit uses just 1 credit. The more you create, the more credits you'll earn! 💫"
        
        else:
            return "I'm excited to help you create stunning video content! 🎥 To get started, please upload your raw video footage or tell me about the amazing content you want to create! 🚀"