// Conversation states
const CONVERSATION_STATES = {
    WELCOME: 'welcome',
    AWAITING_UPLOAD: 'awaiting_upload',
    AWAITING_TEMPLATE: 'awaiting_template',
    AWAITING_REFERENCE_VIDEO: 'awaiting_reference_video',
    AWAITING_INSTRUCTIONS: 'awaiting_instructions',
    PROCESSING: 'processing',
    FINISHED: 'finished'
};

let conversationState = CONVERSATION_STATES.WELCOME;
let selectedTemplate = '';
let uploadedMainVideo = '';
let uploadedReferenceVideo = '';
let processingInterval = null;
let processingStepIndex = -1;

const API_BASE = '/api';

// API Functions
async function sendMessageToBackend(message, history = []) {
    try {
        const response = await fetch(`${API_BASE}/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: history
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: 'Network error' };
    }
}

async function uploadVideoToBackend(file, type = 'main') {
    try {
        const formData = new FormData();
        formData.append('video', file);
        formData.append('type', type);
        
        const response = await fetch(`${API_BASE}/upload/`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    } catch (error) {
        console.error('Upload Error:', error);
        return { success: false, error: 'Upload failed' };
    }
}

// Processing Steps
const PROCESSING_STEPS = [
    { status: "Analyzing speech patterns and video content...", progress: 5 },
    { status: "Removing background noise and silence...", progress: 14 },
    { status: "Applying selected viral template style...", progress: 23 },
    { status: "Generating dynamic captions...", progress: 38 },
    { status: "Synchronizing with background music...", progress: 48 },
    { status: "Inserting B-roll and visual transitions...", progress: 62 },
    { status: "Optimizing color grading and quality...", progress: 68 },
    { status: "Creating viral hooks and callouts...", progress: 78 },
    { status: "Preparing clips for Instagram Reels...", progress: 88 },
    { status: "Final quality check and rendering...", progress: 99 },
];

// UI Functions
function startUpload() {
    hideWelcome();
    addAIMessage("Great! Let's get started. Please upload your raw video footage. You can drag and drop or click to browse.");
    showUploadArea();
    conversationState = 'awaiting_upload';
}

function showTemplates() {
    hideWelcome();
    addAIMessage("Browse and choose a viral template style or create your own:");
    showTemplateSelection();
    conversationState = 'awaiting_template';
}

function showHelp() {
    hideWelcome();
    addAIMessage("I'm here to help! Here's how Zuckky works:\n\n1️⃣ Upload your raw video\n2️⃣ Select your template style\n3️⃣ Add any custom instructions\n4️⃣ Get your professionally edited video in seconds!\n\nWhat would you like to start with?");
}

function hideWelcome() {
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('chatMessages').style.display = 'flex';
}

function showWelcome() {
    document.getElementById('welcomeScreen').style.display = 'block';
    document.getElementById('chatMessages').style.display = 'none';
    document.getElementById('chatMessages').innerHTML = '';
    conversationState = 'welcome';
}

function addAIMessage(text) {
    console.log('🤖 Adding AI message to UI:', text); // Debug log
    
    const messagesContainer = document.getElementById('chatMessages');
    
    // Make sure messages container is visible
    if (messagesContainer.style.display === 'none') {
        messagesContainer.style.display = 'flex';
    }
    
    // Create message element
    const message = document.createElement('div');
    message.className = 'message ai';
    message.innerHTML = `
        <div class="message-content">
            <span class="typing-text"></span>
        </div>
    `;
    
    // Append to container
    messagesContainer.appendChild(message);
    console.log('✅ Message element created and appended'); // Debug log
    
    // Scroll to bottom immediately
    scrollToBottom();
    
    // Typing effect
    const typingElement = message.querySelector('.typing-text');
    let index = 0;
    const typingSpeed = 20; // milliseconds per character
    
    function typeNextChar() {
        if (index < text.length) {
            typingElement.textContent += text.charAt(index);
            index++;
            scrollToBottom();
            setTimeout(typeNextChar, typingSpeed);
        } else {
            console.log('✅ Typing effect completed'); // Debug log
        }
    }
    
    // Start typing effect
    typeNextChar();
}

function addUserMessage(text) {
    const messagesContainer = document.getElementById('chatMessages');
    const message = document.createElement('div');
    message.className = 'message user';
    message.innerHTML = `
        <div class="message-content">${text}</div>
    `;
    messagesContainer.appendChild(message);
    scrollToBottom();
}

function showUploadArea() {
    const messagesContainer = document.getElementById('chatMessages');
    const uploadDiv = document.createElement('div');
    uploadDiv.className = 'message ai';
    uploadDiv.innerHTML = `
        <div class="message-content" style="max-width: 90%;">
            <div class="upload-area" id="uploadArea1">
                <input type="file" id="videoFileInput1" accept="video/*" style="display: none;">
                <div class="upload-icon">📤</div>
                <div class="upload-text">Drop your video here or click to browse</div>
                <div class="upload-subtext">Supports MP4, MOV, AVI up to 2GB</div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(uploadDiv);
    scrollToBottom();
    
    // Setup drag and drop
    const uploadArea = uploadDiv.querySelector('#uploadArea1');
    const fileInput = uploadDiv.querySelector('#videoFileInput1');
    
    uploadArea.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        handleVideoUpload(e, 'main');
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.background = 'rgba(88, 204, 2, 0.15)';
        uploadArea.style.borderColor = '#58CC02';
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.background = 'rgba(88, 204, 2, 0.05)';
        uploadArea.style.borderColor = 'rgba(88, 204, 2, 0.3)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.background = 'rgba(88, 204, 2, 0.05)';
        uploadArea.style.borderColor = 'rgba(88, 204, 2, 0.3)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('video/')) {
            const fakeEvent = { target: { files: files } };
            handleVideoUpload(fakeEvent, 'main');
        }
    });
}

// Update handleVideoUpload to manage state
async function handleVideoUpload(event, type) {
    const file = event.target.files[0];
    if (file) {
        const fileName = file.name;
        const fileSize = (file.size / (1024 * 1024)).toFixed(2);
        
        addUserMessage(`Uploading ${fileName} (${fileSize} MB)...`);
        
        const uploadResult = await uploadVideoToBackend(file, type);
        
        if (uploadResult.success) {
            // Store the file path
            if (type === 'main') {
                uploadedMainVideo = uploadResult.file_path;
            } else if (type === 'reference') {
                uploadedReferenceVideo = uploadResult.file_path;
            }
            
            addUserMessage(`${fileName} uploaded successfully!`);
            
            if (type === 'main') {
                setTimeout(() => {
                    addAIMessage("🎉 Video received! Now, choose your editing style:\n\nWhich viral template would you like to use?");
                    showTemplateSelection();
                    conversationState = CONVERSATION_STATES.AWAITING_TEMPLATE;
                }, 500);
            } else if (type === 'reference') {
                setTimeout(() => {
                    addAIMessage("✅ Reference video received! The AI is now trained with your unique editing style.\n\nWhat specific instructions would you like me to apply to your video?");
                    conversationState = CONVERSATION_STATES.AWAITING_INSTRUCTIONS;
                }, 500);
            }
        } else {
            addAIMessage("Sorry, there was an error uploading your video. Please try again.");
        }
    }
}

function showTemplateSelection() {
    const messagesContainer = document.getElementById('chatMessages');
    const templateDiv = document.createElement('div');
    templateDiv.className = 'message ai';
    templateDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content" style="max-width: 90%;">
            <div class="template-grid">
                <div class="template-card" onclick="selectTemplate('Alex Hormozi')">
                    <div class="template-name">⚡ Alex Hormozi</div>
                    <div class="template-desc">Fast cuts, bold captions, high energy.</div>
                </div>
                <div class="template-card" onclick="selectTemplate('Iman Gadzhi')">
                    <div class="template-name">🎯 Iman Gadzhi</div>
                    <div class="template-desc">Cinematic, smooth B-roll integration.</div>
                </div>
                <div class="template-card" onclick="selectTemplate('Gary Vee')">
                    <div class="template-name">🔥 Gary Vee</div>
                    <div class="template-desc">Raw, authentic feel with subtle cuts.</div>
                </div>
                <div class="template-card custom-style" onclick="selectTemplate('Custom')">
                    <div class="template-name">✨ Create Your Own Unique Style</div>
                    <div class="template-desc">Train the AI with your reference video.</div>
                </div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(templateDiv);
    scrollToBottom();
}

// Update your selectTemplate function to manage state properly
function selectTemplate(template) {
    selectedTemplate = template;
    addUserMessage(`${template} Style Selected`);
    
    if (template === 'Custom') {
        setTimeout(() => {
            addAIMessage("Awesome choice! Creating a custom style makes your content unique. Please upload a reference video that has the editing style you want to replicate.");
            showReferenceVideoUpload();
            conversationState = CONVERSATION_STATES.AWAITING_REFERENCE_VIDEO;
        }, 500);
    } else {
        setTimeout(() => {
            addAIMessage(`Perfect! The ${template} style is amazing for viral content! 🎯\n\nNow, what specific instructions would you like me to apply? For example:\n• Add dynamic captions\n• Include background music\n• Create quick cuts\n• Add transitions\n• Any other special requests?`);
            conversationState = CONVERSATION_STATES.AWAITING_INSTRUCTIONS;
        }, 500);
    }
}

function showReferenceVideoUpload() {
    const messagesContainer = document.getElementById('chatMessages');
    const uploadDiv = document.createElement('div');
    uploadDiv.className = 'message ai';
    uploadDiv.innerHTML = `
        <div class="message-content" style="max-width: 90%;">
            <div class="upload-area" id="uploadArea2">
                <input type="file" id="videoFileInput2" accept="video/*" style="display: none;">
                <div class="upload-icon">📤</div>
                <div class="upload-text">Drop your reference video here or click to browse</div>
                <div class="upload-subtext">Upload an existing video with your desired editing style</div>
            </div>
        </div>
    `;
    messagesContainer.appendChild(uploadDiv);
    scrollToBottom();
    
    // Setup drag and drop
    const uploadArea = uploadDiv.querySelector('#uploadArea2');
    const fileInput = uploadDiv.querySelector('#videoFileInput2');
    
    uploadArea.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        handleVideoUpload(e, 'reference');
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.background = 'rgba(88, 204, 2, 0.15)';
        uploadArea.style.borderColor = '#58CC02';
    });
    
    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.background = 'rgba(88, 204, 2, 0.05)';
        uploadArea.style.borderColor = 'rgba(88, 204, 2, 0.3)';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadArea.style.background = 'rgba(88, 204, 2, 0.05)';
        uploadArea.style.borderColor = 'rgba(88, 204, 2, 0.3)';
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('video/')) {
            const fakeEvent = { target: { files: files } };
            handleVideoUpload(fakeEvent, 'reference');
        }
    });
}

function getDetailedProgressHTML() {
    return `
        <div class="message ai" id="processingMessage">
            <div class="message-avatar">🤖</div>
            <div class="message-content" style="max-width: 90%;">
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressBarFill" style="width: 0%"></div>
                    </div>
                    
                    <div class="progress-details-header">
                        <div class="progress-status" id="progressStatus">🎬 Starting AI Edit...</div>
                        <button class="progress-toggle-btn" onclick="toggleProgressDetails(event)">
                            <svg id="toggleIcon" style="transform: rotate(180deg);" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-down"><polyline points="6 9 12 15 18 9"></polyline></svg>
                        </button>
                    </div>

                    <div class="progress-time" id="progressTime">0% Complete</div>

                    <ul class="progress-step-list open" id="progressStepList">
                        ${PROCESSING_STEPS.map((step, index) => `
                            <li class="progress-step-item" data-step-index="${index}" id="step-${index}">
                                <span class="step-icon">⚪</span>
                                <span>${step.status}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
}

function toggleProgressDetails(event) {
    event.stopPropagation();

    const list = document.getElementById('progressStepList');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (list.classList.contains('open')) {
        list.classList.remove('open');
        toggleIcon.style.transform = 'rotate(0deg)';
    } else {
        list.classList.add('open');
        toggleIcon.style.transform = 'rotate(180deg)';
    }
}

function startSequentialProcessing() {
    if (processingInterval) clearInterval(processingInterval);
    
    const messagesContainer = document.getElementById('chatMessages');

    messagesContainer.insertAdjacentHTML('beforeend', getDetailedProgressHTML());
    scrollToBottom();

    processingStepIndex = -1;
    const totalSteps = PROCESSING_STEPS.length;
    const intervalDuration = 800;

    processingInterval = setInterval(() => {
        const fillEl = document.getElementById('progressBarFill');
        const statusEl = document.getElementById('progressStatus');
        const timeEl = document.getElementById('progressTime');
        
        if (!fillEl || !statusEl || !timeEl) {
            clearInterval(processingInterval);
            return;
        }
        
        if (processingStepIndex >= 0 && processingStepIndex < totalSteps) {
            const prevStepEl = document.getElementById(`step-${processingStepIndex}`);
            if (prevStepEl) {
                prevStepEl.classList.remove('active');
                prevStepEl.classList.add('completed');
                prevStepEl.querySelector('.step-icon').innerHTML = '✅';
            }
        }
        
        processingStepIndex++;
        
        if (processingStepIndex < totalSteps) {
            const currentStep = PROCESSING_STEPS[processingStepIndex];
            
            fillEl.style.width = `${currentStep.progress}%`;
            timeEl.textContent = `${currentStep.progress}% Complete`;

            statusEl.textContent = `🎬 ${currentStep.status}`;

            const currentStepEl = document.getElementById(`step-${processingStepIndex}`);
            if (currentStepEl) {
                currentStepEl.classList.add('active');
                currentStepEl.querySelector('.step-icon').innerHTML = '⚡';
            }
            
        } else {
            clearInterval(processingInterval);
            fillEl.style.width = '100%';
            
            statusEl.textContent = '✅ Video Editing Complete!';
            timeEl.textContent = '100% Complete 🎉';

            setTimeout(() => {
                const finalMsg = document.createElement('div');
                finalMsg.className = 'message ai';
                finalMsg.innerHTML = `
                    <div class="message-avatar">🤖</div>
                    <div class="message-content">Your Viral Video is ready! <br><br>
                    <a href="#" style="color:#58CC02; text-decoration: underline;">➡️ Click to View Final Edit</a> | 
                    <a href="#" style="color:#58CC02; text-decoration: underline;">⬇️ Download Video (MP4)</a>
                    </div>
                `;
                messagesContainer.appendChild(finalMsg);
                scrollToBottom();
                conversationState = 'finished';
            }, 1000); 
        }

    }, intervalDuration);
}

// Main Chat Function
// Update your sendMessage function to handle specific states
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (message) {
        addUserMessage(message);
        input.value = '';
        
        console.log(`📤 State: ${conversationState}, Message: ${message}`);
        
        // Handle specific conversation states locally without calling Gemini
        if (conversationState === CONVERSATION_STATES.AWAITING_INSTRUCTIONS) {
            handleEditingInstructions(message);
            return;
        }
        
        if (conversationState === CONVERSATION_STATES.AWAITING_TEMPLATE) {
            handleTemplateSelection(message);
            return;
        }
        
        // For other states, use Gemini
        try {
            const response = await sendMessageToBackend(message);
            
            if (response.success) {
                addAIMessage(response.response);
                conversationState = response.conversation_state || conversationState;
            } else {
                addAIMessage("Let's continue with your video edit! What would you like to do next?");
            }
        } catch (error) {
            console.error('❌ Network error:', error);
            handleFallbackResponse(message);
        }
    }
}

// Utility Functions
function handleAction(action) {
    console.log(`Action requested: ${action}`);
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function scrollToBottom() {
    const container = document.getElementById('chatContainer');
    if (container) {
        container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
        });
        console.log('📜 Scrolled to bottom'); // Debug log
    }
}

// Auto-resize textarea
const textarea = document.getElementById('chatInput');
textarea.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
});

// Handle template selection from text input
function handleTemplateSelection(message) {
    const messageLower = message.toLowerCase();
    
    if (messageLower.includes('alex') || messageLower.includes('hormozi')) {
        selectTemplate('Alex Hormozi');
    } else if (messageLower.includes('iman') || messageLower.includes('gadzhi')) {
        selectTemplate('Iman Gadzhi');
    } else if (messageLower.includes('gary') || messageLower.includes('vee')) {
        selectTemplate('Gary Vee');
    } else if (messageLower.includes('custom')) {
        selectTemplate('Custom');
    } else {
        // If we can't determine, show templates again
        addAIMessage("I'm not sure which style you meant. Please select from these viral templates:");
        showTemplateSelection();
    }
}

// Start the actual video processing
function startVideoProcessing(instructions = '') {
    console.log('🚀 Starting video processing with:', {
        mainVideo: uploadedMainVideo,
        referenceVideo: uploadedReferenceVideo,
        template: selectedTemplate,
        instructions: instructions
    });
    
    // Show processing UI
    startSequentialProcessing();
    conversationState = CONVERSATION_STATES.PROCESSING;
    
    // In a real app, you would call your video processing API here
    // For now, we'll use the simulated processing
}

// Start the actual video processing
function startVideoProcessing(instructions = '') {
    console.log('🚀 Starting video processing with:', {
        mainVideo: uploadedMainVideo,
        referenceVideo: uploadedReferenceVideo,
        template: selectedTemplate,
        instructions: instructions
    });
    
    // Show processing UI
    startSequentialProcessing();
    conversationState = CONVERSATION_STATES.PROCESSING;
    
    // In a real app, you would call your video processing API here
    // For now, we'll use the simulated processing
}

// Fallback for when Gemini is not available
function handleFallbackResponse(message) {
    const messageLower = message.toLowerCase();
    
    if (conversationState === CONVERSATION_STATES.WELCOME) {
        if (messageLower.includes('upload') || messageLower.includes('video')) {
            startUpload();
        } else if (messageLower.includes('template') || messageLower.includes('style')) {
            showTemplates();
        } else {
            addAIMessage("Welcome to Zuckky! I can help you create amazing viral videos. Would you like to upload a video or browse templates?");
        }
    } else {
        addAIMessage("Let's continue with your video edit! What would you like to do next?");
    }
}

// Handle editing instructions without calling Gemini
function handleEditingInstructions(instructions) {
    console.log('🎬 Processing editing instructions:', instructions);
    
    // Store the instructions and start processing
    addAIMessage(`Got it! I'll apply these instructions: "${instructions}". Starting the video editing process now... 🚀`);
    
    // Start the video processing
    startVideoProcessing(instructions);
}