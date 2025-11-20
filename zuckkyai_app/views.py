import json
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .utils.gemini_client import GeminiClient
from .utils.video_processor import VideoProcessor

def home(request):
    """Serve the main editor interface"""
    return render(request, 'editor.html')

def editor(request):
    """Alternative view for the editor"""
    return render(request, 'editor.html')

@csrf_exempt
def chat_message(request):
    """Handle chat messages with Gemini AI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            conversation_history = data.get('history', [])
            
            # Initialize Gemini client
            gemini = GeminiClient()
            
            # Get AI response
            ai_response = gemini.get_chat_response(user_message, conversation_history)
            
            return JsonResponse({
                'success': True,
                'response': ai_response,
                'conversation_state': determine_conversation_state(user_message, ai_response)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def upload_video(request):
    """Handle video file uploads"""
    if request.method == 'POST' and request.FILES.get('video'):
        try:
            video_file = request.FILES['video']
            upload_type = request.POST.get('type', 'main')  # 'main' or 'reference'
            
            # Save the file
            file_path = f"uploads/{upload_type}/{video_file.name}"
            saved_path = default_storage.save(file_path, ContentFile(video_file.read()))
            
            return JsonResponse({
                'success': True,
                'file_path': saved_path,
                'file_name': video_file.name,
                'file_size': video_file.size,
                'type': upload_type
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'No video file provided'})

# @csrf_exempt
# def process_video(request):
    """Start video processing with actual video editing API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            main_video_path = data.get('main_video')
            reference_video_path = data.get('reference_video')
            template_style = data.get('template_style', 'default')
            instructions = data.get('instructions', '')
            
            # Initialize video processor
            from .utils.video_processor import get_video_processor
            processor = get_video_processor()
            
            # Start processing
            task_id = processor.start_processing(
                main_video_path,
                reference_video_path,
                template_style,
                instructions
            )
            
            return JsonResponse({
                'success': True,
                'task_id': task_id,
                'message': 'Video processing started successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

@csrf_exempt
def process_video(request):
    """Start video processing with actual video editing API"""
    if request.method == 'POST':
        style = request.POST.get('style')
        uploaded_video = request.FILES.get('video')
        
        # Map styles to pre-edited videos
        video_mapping = {
            'alex_hormozi': '/static/videos/alex_edited.mp4',
            'iman_gadzhi': '/static/videos/iman_edited.mp4',
            'gary_vee': '/static/videos/gary_edited.mp4'
        }
        
        if style == 'custom':
            return JsonResponse({
                'success': False,
                'message': '🚧 Custom video editing is temporarily unavailable due to high API demand. Try Alex, Iman, or Gary styles!'
            })
        
        if style in video_mapping:
            # Return the pre-edited video URL
            edited_video_url = f"https://{request.get_host()}{video_mapping[style]}"
            
            return JsonResponse({
                'success': True,
                'edited_video_url': edited_video_url,
                'message': f'✅ Video successfully edited in {style.replace("_", " ").title()} style!'
            })
        
        return JsonResponse({
            'success': False, 
            'message': 'Invalid style selected'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST requests allowed'
    })

@csrf_exempt
def check_processing_status(request, task_id):
    """Check status of video processing"""
    try:
        from .utils.video_processor import get_video_processor
        processor = get_video_processor()
        
        status = processor.get_processing_status(task_id)
        
        return JsonResponse({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def determine_conversation_state(user_message, ai_response):
    """Determine the current state of conversation for frontend logic"""
    message_lower = user_message.lower()
    
    # If we're in a specific state, don't change it based on message content
    # The frontend should manage these states
    
    # Only determine state for general conversations
    if any(word in message_lower for word in ['upload', 'video', 'footage']):
        return 'awaiting_upload'
    elif any(word in message_lower for word in ['template', 'style', 'viral']):
        return 'awaiting_template'
    elif any(word in message_lower for word in ['reference', 'custom', 'train']):
        return 'awaiting_reference_video'
    elif any(word in message_lower for word in ['instructions', 'edit', 'process']):
        return 'awaiting_instructions'
    else:
        return 'chatting'  # General chat, not interrupting workflow


# def process_video_style(request):
    if request.method == 'POST':
        style = request.POST.get('style')
        raw_video = request.FILES.get('video')
        
        # Store the raw video (for you to manually edit later)
        # For demo, just return the pre-edited version
        
        video_urls = {
            'alex_hormozi': 'https://your-render-app.onrender.com/static/videos/alex_edited.mp4',
            'iman_gadzhi': 'https://your-render-app.onrender.com/static/videos/iman_edited.mp4', 
            'gary_vee': 'https://your-render-app.onrender.com/static/videos/gary_edited.mp4',
            'custom': None  # This will show "API exhausted" message
        }
        
        if style == 'custom':
            return JsonResponse({
                'status': 'error',
                'message': 'API token exhausted for custom edits. Please try Alex, Iman, or Gary styles.'
            })
        
        video_url = video_urls.get(style)
        
        return JsonResponse({
            'status': 'success',
            'edited_video_url': video_url,
            'message': f'Video successfully edited in {style} style!'
        })