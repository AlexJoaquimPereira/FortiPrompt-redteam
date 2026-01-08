"""
FortiPrompt Target Interface
Connects to your existing SimpleRagChatBot backend
File: FortiPrompt/core/target_interface.py
"""

import requests
import json
import time
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class ConversationMessage:
    """Represents a message in conversation history"""
    role: str
    content: str
    timestamp: str


class TargetSystemInterface:
    """
    Interface to your existing RAG chatbot backend
    Adapts FortiPrompt to work with your SimpleRagChatBotBackend
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        model_id: str = None
    ):
        """
        Initialize connection to your RAG backend
        
        Args:
            base_url: URL where your main.py backend is running
            timeout: Request timeout in seconds
            model_id: Model to use (auto-detects if None)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.conversation_history = []
        
        # Auto-detect or use provided model
        if model_id:
            self.model_id = model_id
        else:
            # Try to get available models from backend
            self.model_id = self._detect_available_model()
        
        print(f"[TargetInterface] Using model: {self.model_id}")
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test if backend is accessible"""
        try:
            # Your backend uses /docs or root endpoint, not /health
            # Try multiple endpoints to detect if it's running
            endpoints_to_try = [
                "/docs",  # FastAPI docs
                "/",      # Root
                "/chat"   # Your actual chat endpoint
            ]
            
            connected = False
            for endpoint in endpoints_to_try:
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=3
                    )
                    if response.status_code in [200, 404, 405, 422]:  # Any valid HTTP response
                        connected = True
                        break
                except:
                    continue
            
            if connected:
                print(f"✓ Connected to target system at {self.base_url}")
            else:
                raise Exception("Cannot connect")
                
        except:
            print(f"⚠ Warning: Could not connect to {self.base_url}")
            print("  Make sure your backend is running:")
            print("  cd SimpleRagChatBotBackend && python main.py")
    
    def _detect_available_model(self) -> str:
        """
        Detect which model is actually available in your backend
        Checks /config endpoint or tries common models
        """
        try:
            # Try to get config from backend
            response = self.session.get(f"{self.base_url}/config", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                if models:
                    print(f"[TargetInterface] Available models: {models}")
                    # Prioritize Ollama models (free and local)
                    for model in models:
                        if model.lower() in ['llama31', 'mistral', 'qwen']:
                            return model
                    # Return first available
                    return models[0]
        except Exception as e:
            print(f"[TargetInterface] Could not fetch models: {e}")
        
        # Fallback: Try common model names
        test_models = ['Llama31', 'Mistral', 'Qwen', 'Gpt4', 'Gemini', 'Claude']
        
        for model in test_models:
            try:
                response = self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": "test",
                        "user_id": "fortiprompt_test",
                        "model_id": model
                    },
                    timeout=5
                )
                if response.status_code in [200, 422]:  # 422 might be validation, but model exists
                    # Check if error is about model not found
                    if response.status_code == 422:
                        error = response.json().get('detail', '')
                        if 'model' not in str(error).lower():
                            return model
                    else:
                        return model
            except:
                continue
        
        # Last resort fallback
        print("[TargetInterface] Warning: Could not detect model, using 'Llama31'")
        return 'Llama31'
    
    def query(
        self, 
        prompt: str, 
        context: str = None,
        conversation_id: str = None,
        model_id: str = None
    ) -> str:
        """
        Query your RAG chatbot with optional context injection
        
        Args:
            prompt: User query/attack prompt
            context: Optional RAG context (for document poisoning tests)
            conversation_id: Optional conversation ID (not used by your backend)
            model_id: Model to use (uses self.model_id if not specified)
            
        Returns:
            Response from your RAG system
        """
        
        # Use instance model_id if not specified
        model_to_use = model_id or self.model_id
        
        # YOUR BACKEND REQUIRES (from main.py ChatRequest):
        # - message: str (required)
        # - user_id: str (required)
        # - model_id: str (required) - must be one of available models
        # - use_memory: bool (optional, default False)
        # - history: Optional[List[dict]] (optional)
        
        endpoint = f"{self.base_url}/chat"
        
        # Build payload matching your backend's ChatRequest model
        payload = {
            "message": prompt,
            "user_id": "fortiprompt_redteam",
            "model_id": model_to_use,
            "use_memory": False,  # Don't use memory for red team tests
            "history": []  # Empty history for each test
        }
        
        # Note: Your backend doesn't support context injection yet
        # You would need to modify rag_agent.py to support this for RAG poisoning tests
        if context:
            # This won't work with current backend, but keeping for future
            payload["_note"] = "Context injection not supported by backend yet"
        
        try:
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract response based on ChatResponse model
            # Your backend returns: {"response": str, "tool_used": Optional[str]}
            if isinstance(data, dict):
                response_text = data.get("response", str(data))
            else:
                response_text = str(data)
            
            # Store in conversation history
            self.conversation_history.append({
                "prompt": prompt,
                "response": response_text,
                "timestamp": time.time(),
                "model_id": model_to_use
            })
            
            return response_text
            
        except requests.exceptions.Timeout:
            return "Error: Request timeout - backend may be overloaded (120s timeout)"
        
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to backend - is it running on port 8000?"
        
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_json = e.response.json()
                error_detail = error_json.get('detail', str(error_json))
                
                # Check if it's a model not found error
                if 'model' in str(error_detail).lower() and 'not found' in str(error_detail).lower():
                    # Try to extract which models are available
                    return f"Error: Model '{model_to_use}' not available. Check /config endpoint for available models."
                    
            except:
                error_detail = e.response.text[:200]
            return f"Error: HTTP {e.response.status_code} - {error_detail}"
        
        except Exception as e:
            return f"Error: {type(e).__name__} - {str(e)}"
    
    def query_with_poisoned_doc(
        self,
        prompt: str,
        poisoned_doc_content: str,
        doc_title: str = "HR Document"
    ) -> str:
        """
        Query with a poisoned document in RAG context
        
        This requires modifying your backend to accept injected documents
        OR uploading the document to your data/ folder before testing
        
        Args:
            prompt: User query
            poisoned_doc_content: Content of poisoned document
            doc_title: Document title
            
        Returns:
            Response from system
        """
        
        # Option 1: If your backend supports context injection
        return self.query(prompt, context=poisoned_doc_content)
        
        # Option 2: Upload document to backend (if you add this API)
        # upload_endpoint = f"{self.base_url}/upload_document"
        # files = {"file": (doc_title, poisoned_doc_content)}
        # self.session.post(upload_endpoint, files=files)
        # return self.query(prompt)
    
    def reset_conversation(self):
        """Reset conversation state"""
        self.conversation_history = []
        
        # If your backend has conversation reset endpoint
        try:
            self.session.post(f"{self.base_url}/reset")
        except:
            pass
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history for analysis"""
        return self.conversation_history
    
    def test_basic_functionality(self) -> bool:
        """
        Test basic functionality with safe queries
        Returns True if backend responds correctly
        """
        test_queries = [
            "Hello, how are you?",
            "What can you help me with?",
            "Tell me about employee benefits"
        ]
        
        print("\n[Testing Backend Functionality]")
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            response = self.query(query)
            print(f"Response: {response[:100]}...")
            
            if "Error" in response:
                print("✗ Backend test failed")
                return False
            
            time.sleep(1)  # Rate limiting
        
        print("\n✓ Backend functioning correctly")
        return True


class EnhancedTargetInterface(TargetSystemInterface):
    """
    Enhanced interface with additional monitoring capabilities
    Useful for detailed analysis during testing
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_count = 0
        self.error_count = 0
        self.response_times = []
    
    def query(self, prompt: str, context: str = None, **kwargs) -> str:
        """Enhanced query with timing and error tracking"""
        
        self.query_count += 1
        start_time = time.time()
        
        response = super().query(prompt, context, **kwargs)
        
        elapsed = time.time() - start_time
        self.response_times.append(elapsed)
        
        if "Error" in response:
            self.error_count += 1
        
        return response
    
    def get_statistics(self) -> Dict:
        """Get query statistics"""
        return {
            "total_queries": self.query_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / self.query_count if self.query_count > 0 else 0,
            "avg_response_time": sum(self.response_times) / len(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0
        }
    
    def print_statistics(self):
        """Print query statistics"""
        stats = self.get_statistics()
        print("\n" + "="*50)
        print("TARGET SYSTEM STATISTICS")
        print("="*50)
        print(f"Total Queries: {stats['total_queries']}")
        print(f"Errors: {stats['error_count']} ({stats['error_rate']:.1%})")
        print(f"Avg Response Time: {stats['avg_response_time']:.2f}s")
        print(f"Max Response Time: {stats['max_response_time']:.2f}s")
        print("="*50)


# Backend Integration Helper
class BackendIntegrationHelper:
    """
    Helper class for integrating FortiPrompt with your backend
    Provides utilities for testing and configuration
    """
    
    @staticmethod
    def check_backend_running(base_url: str = "http://localhost:8000") -> bool:
        """Check if your backend is running"""
        try:
            # Try multiple endpoints
            for endpoint in ["/docs", "/", "/chat"]:
                try:
                    response = requests.get(f"{base_url}{endpoint}", timeout=3)
                    if response.status_code in [200, 404, 405, 422]:
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    @staticmethod
    def get_backend_info(base_url: str = "http://localhost:8000") -> Dict:
        """Get information about your backend"""
        try:
            response = requests.get(f"{base_url}/info", timeout=5)
            return response.json()
        except:
            return {"error": "Could not fetch backend info"}
    
    @staticmethod
    def upload_test_document(
        base_url: str,
        doc_content: str,
        filename: str = "test_doc.txt"
    ) -> bool:
        """
        Upload a test document to your backend
        Requires implementing upload endpoint in your main.py
        """
        try:
            endpoint = f"{base_url}/upload"
            files = {"file": (filename, doc_content)}
            response = requests.post(endpoint, files=files)
            return response.status_code == 200
        except:
            return False


# Testing function
def test_integration():
    """
    Test integration with your RAG backend
    Run this to verify FortiPrompt can communicate with your system
    """
    print("="*60)
    print("FORTIPROMPT BACKEND INTEGRATION TEST")
    print("="*60)
    
    # Check if backend is running
    helper = BackendIntegrationHelper()
    
    print("\n[1/3] Checking if backend is running...")
    if not helper.check_backend_running():
        print("✗ Backend not running!")
        print("\nPlease start your backend:")
        print("  cd SimpleRagChatBotBackend")
        print("  python main.py")
        return False
    
    print("✓ Backend is running")
    
    # Create interface
    print("\n[2/3] Creating target interface...")
    interface = EnhancedTargetInterface()
    
    # Test basic functionality
    print("\n[3/3] Testing basic functionality...")
    success = interface.test_basic_functionality()
    
    if success:
        print("\n" + "="*60)
        print("✓ INTEGRATION TEST PASSED")
        print("="*60)
        print("\nYou can now run FortiPrompt red team tests!")
        print("Example: python main.py --test basic")
        
        interface.print_statistics()
        return True
    else:
        print("\n✗ Integration test failed")
        return False


if __name__ == "__main__":
    # Run integration test
    test_integration()