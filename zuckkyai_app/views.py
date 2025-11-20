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

@csrf_exempt
def process_video(request):
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