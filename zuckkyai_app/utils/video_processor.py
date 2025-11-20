import requests
import time
import os
import json
from django.conf import settings
from django.core.files.storage import default_storage

class VideoProcessor:
    def __init__(self):
        # For hackathon demo - you can use mock or real APIs
        self.api_base_url = getattr(settings, 'VIDEO_API_URL', 'https://api.runwayml.com/v1')  # Example API
        self.api_key = getattr(settings, 'VIDEO_API_KEY', 'your-api-key-here')
        self.mock_mode = getattr(settings, 'MOCK_VIDEO_PROCESSING', True)  # Use mock for demo
        
    def start_processing(self, main_video_path, reference_video_path=None, template_style='default', instructions=''):
        """
        Start video processing with the selected parameters
        Returns a task ID that can be used to check status
        """
        if self.mock_mode:
            return self._mock_start_processing(main_video_path, reference_video_path, template_style, instructions)
        else:
            return self._real_start_processing(main_video_path, reference_video_path, template_style, instructions)
    
    def _mock_start_processing(self, main_video_path, reference_video_path, template_style, instructions):
        """
        Mock processing for hackathon demo
        Simulates API calls and returns a mock task ID
        """
        print(f"🎬 MOCK: Starting video processing")
        print(f"   Main Video: {main_video_path}")
        print(f"   Reference Video: {reference_video_path}")
        print(f"   Template Style: {template_style}")
        print(f"   Instructions: {instructions}")
        
        # Simulate API delay
        time.sleep(1)
        
        # Generate a unique task ID
        task_id = f"mock_task_{int(time.time())}_{hash(main_video_path) % 10000}"
        
        # Store processing details (in real app, this would be in database)
        processing_details = {
            'task_id': task_id,
            'main_video': main_video_path,
            'reference_video': reference_video_path,
            'template_style': template_style,
            'instructions': instructions,
            'status': 'processing',
            'progress': 0,
            'started_at': time.time(),
            'estimated_completion': time.time() + 30  # 30 seconds from now
        }
        
        # In a real app, you'd save this to database
        self._save_processing_details(task_id, processing_details)
        
        return task_id
    
    def _real_start_processing(self, main_video_path, reference_video_path, template_style, instructions):
        """
        Real implementation for actual video editing API
        This would integrate with services like RunwayML, FFmpeg, or custom AI models
        """
        try:
            # Prepare video files for API
            main_video_url = self._prepare_video_for_api(main_video_path)
            reference_video_url = None
            if reference_video_path:
                reference_video_url = self._prepare_video_for_api(reference_video_path)
            
            # Map template styles to API parameters
            style_params = self._map_template_to_parameters(template_style)
            
            # Prepare API payload
            payload = {
                'input_video': main_video_url,
                'output_format': 'mp4',
                'quality': 'high',
                'style_preset': style_params,
                'user_instructions': instructions,
                'callback_url': f"{settings.BASE_URL}/api/processing_callback/"  # For webhooks
            }
            
            if reference_video_url:
                payload['reference_video'] = reference_video_url
                payload['style_transfer'] = True
            
            # Headers for authentication
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            print(f"🚀 Sending to Video API: {self.api_base_url}/process")
            
            # Make API call to video editing service
            response = requests.post(
                f"{self.api_base_url}/process",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')
                
                # Store processing details
                processing_details = {
                    'task_id': task_id,
                    'main_video': main_video_path,
                    'reference_video': reference_video_path,
                    'template_style': template_style,
                    'instructions': instructions,
                    'status': 'submitted',
                    'progress': 0,
                    'started_at': time.time(),
                    'api_response': data
                }
                
                self._save_processing_details(task_id, processing_details)
                return task_id
                
            else:
                error_msg = f"Video API error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except Exception as e:
            print(f"❌ Error in real video processing: {str(e)}")
            # Fall back to mock mode if real API fails
            return self._mock_start_processing(main_video_path, reference_video_path, template_style, instructions)
    
    def get_processing_status(self, task_id):
        """
        Check status of video processing
        """
        if self.mock_mode:
            return self._mock_get_status(task_id)
        else:
            return self._real_get_status(task_id)
    
    def _mock_get_status(self, task_id):
        """
        Mock status checking - simulates progress
        """
        try:
            # Get processing details (in real app, from database)
            details = self._get_processing_details(task_id)
            if not details:
                return {'status': 'error', 'progress': 0, 'error': 'Task not found'}
            
            # Simulate progress
            elapsed = time.time() - details['started_at']
            total_estimated = 30  # 30 seconds total for mock
            
            if elapsed >= total_estimated:
                progress = 100
                status = 'completed'
                download_url = f"/media/processed/{task_id}_final.mp4"
            else:
                progress = min(95, int((elapsed / total_estimated) * 100))
                status = 'processing'
                download_url = None
            
            # Update details
            details['progress'] = progress
            details['status'] = status
            if download_url:
                details['download_url'] = download_url
            
            self._save_processing_details(task_id, details)
            
            return {
                'status': status,
                'progress': progress,
                'download_url': download_url,
                'estimated_seconds_remaining': max(0, total_estimated - elapsed)
            }
            
        except Exception as e:
            return {'status': 'error', 'progress': 0, 'error': str(e)}
    
    def _real_get_status(self, task_id):
        """
        Real implementation for checking status with actual API
        """
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(
                f"{self.api_base_url}/status/{task_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                api_data = response.json()
                
                # Update our local storage
                details = self._get_processing_details(task_id)
                if details:
                    details['status'] = api_data.get('status', 'unknown')
                    details['progress'] = api_data.get('progress', 0)
                    details['api_status'] = api_data
                    self._save_processing_details(task_id, details)
                
                return api_data
            else:
                return {'status': 'error', 'progress': 0, 'error': f"API status check failed: {response.status_code}"}
                
        except Exception as e:
            return {'status': 'error', 'progress': 0, 'error': str(e)}
    
    def get_download_url(self, task_id):
        """
        Get download URL for processed video
        """
        if self.mock_mode:
            # For mock, return a simulated download URL
            return f"/media/processed/{task_id}_final.mp4"
        else:
            try:
                headers = {'Authorization': f'Bearer {self.api_key}'}
                response = requests.get(
                    f"{self.api_base_url}/download/{task_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('download_url')
                else:
                    return None
                    
            except Exception as e:
                print(f"Error getting download URL: {e}")
                return None
    
    def _prepare_video_for_api(self, file_path):
        """
        Prepare video file for API consumption
        In production, this would upload to cloud storage and return URL
        """
        if file_path.startswith('http'):
            return file_path  # Already a URL
            
        # For local files during hackathon, we might need to use a service like ngrok
        # or upload to temporary cloud storage
        if self.mock_mode:
            return f"file://{file_path}"  # Mock URL
        else:
            # Upload to cloud storage and return URL
            return self._upload_to_cloud_storage(file_path)
    
    def _upload_to_cloud_storage(self, file_path):
        """
        Upload file to cloud storage (S3, GCS, etc.) and return public URL
        For hackathon, you might skip this or use a simple solution
        """
        # This is a placeholder - implement based on your cloud storage
        try:
            # Example for AWS S3
            # import boto3
            # s3 = boto3.client('s3')
            # s3.upload_file(file_path, 'your-bucket', f"uploads/{os.path.basename(file_path)}")
            # return f"https://your-bucket.s3.amazonaws.com/uploads/{os.path.basename(file_path)}"
            
            # For hackathon demo, return a mock URL
            return f"https://your-storage.com/videos/{os.path.basename(file_path)}"
        except Exception as e:
            print(f"Cloud storage upload error: {e}")
            return f"file://{file_path}"  # Fallback
    
    def _map_template_to_parameters(self, template_style):
        """
        Map human-readable template names to API parameters
        """
        template_mappings = {
            'Alex Hormozi': {
                'style': 'fast_cuts',
                'caption_style': 'bold',
                'pace': 'high',
                'music_tempo': 'upbeat'
            },
            'Iman Gadzhi': {
                'style': 'cinematic',
                'transitions': 'smooth',
                'color_grade': 'cinematic',
                'pace': 'medium'
            },
            'Gary Vee': {
                'style': 'authentic',
                'cuts': 'minimal',
                'color_grade': 'natural',
                'pace': 'conversational'
            },
            'Custom': {
                'style': 'custom',
                'style_transfer': True
            },
            'default': {
                'style': 'professional',
                'pace': 'medium',
                'color_grade': 'enhanced'
            }
        }
        
        return template_mappings.get(template_style, template_mappings['default'])
    
    def _save_processing_details(self, task_id, details):
        """
        Save processing details to temporary storage
        In production, use database. For hackathon, using file storage.
        """
        try:
            storage_path = f"processing_tasks/{task_id}.json"
            with default_storage.open(storage_path, 'w') as f:
                json.dump(details, f)
        except Exception as e:
            print(f"Error saving processing details: {e}")
    
    def _get_processing_details(self, task_id):
        """
        Retrieve processing details from storage
        """
        try:
            storage_path = f"processing_tasks/{task_id}.json"
            if default_storage.exists(storage_path):
                with default_storage.open(storage_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading processing details: {e}")
        
        return None
    
    def cancel_processing(self, task_id):
        """
        Cancel ongoing video processing
        """
        if not self.mock_mode:
            try:
                headers = {'Authorization': f'Bearer {self.api_key}'}
                response = requests.post(
                    f"{self.api_base_url}/cancel/{task_id}",
                    headers=headers
                )
                return response.status_code == 200
            except Exception as e:
                print(f"Error canceling task: {e}")
        
        # For mock mode or if real cancel fails, just mark as canceled
        details = self._get_processing_details(task_id)
        if details:
            details['status'] = 'canceled'
            self._save_processing_details(task_id, details)
            return True
        
        return False

# Utility function to create video processor instance
def get_video_processor():
    return VideoProcessor()