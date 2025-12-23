import json
import requests
import base64
from wasmtime import Linker, Module, Store
import ctypes
import struct
from .config import Config
from .display import print_status, print_response_start, stream_live

class DeepSeekClient:
    def __init__(self):
        self.config = Config()
        self.cookies = self._load_cookies()
        self.token = self._load_token()
        self.session_id = None  # keep session alive
        self.parent_message_id = None  # track conversation
    
    def _load_cookies(self):
        """grab cookies from file if they exist"""
        try:
            with open(self.config.COOKIES_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_token(self):
        """get our auth token"""
        try:
            with open(self.config.TOKEN_FILE, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def _compute_pow_answer(self, challenge_str, salt, difficulty, expire_at):
        """solve the proof of work challenge (this is the tricky part)"""
        prefix = f"{salt}_{expire_at}_"
        store = Store()
        linker = Linker(store.engine)
        
        with open(self.config.WASM_FILE, "rb") as f:
            wasm_bytes = f.read()
        
        module = Module(store.engine, wasm_bytes)
        instance = linker.instantiate(store, module)
        exports = instance.exports(store)
        
        memory = exports["memory"]
        add_to_stack = exports["__wbindgen_add_to_stack_pointer"]
        alloc = exports["__wbindgen_export_0"]
        wasm_solve = exports["wasm_solve"]
        
        def write_memory(offset, data):
            base_addr = ctypes.cast(memory.data_ptr(store), ctypes.c_void_p).value
            ctypes.memmove(base_addr + offset, data, len(data))
        
        def read_memory(offset, size):
            base_addr = ctypes.cast(memory.data_ptr(store), ctypes.c_void_p).value
            return ctypes.string_at(base_addr + offset, size)
        
        def encode_string(text):
            data = text.encode("utf-8")
            ptr_val = alloc(store, len(data), 1)
            ptr = int(ptr_val.value) if hasattr(ptr_val, "value") else int(ptr_val)
            write_memory(ptr, data)
            return ptr, len(data)
        
        retptr = add_to_stack(store, -16)
        ptr_challenge, len_challenge = encode_string(challenge_str)
        ptr_prefix, len_prefix = encode_string(prefix)
        
        wasm_solve(store, retptr, ptr_challenge, len_challenge, ptr_prefix, len_prefix, float(difficulty))
        
        status = struct.unpack("<i", read_memory(retptr, 4))[0]
        value = struct.unpack("<d", read_memory(retptr + 8, 8))[0]
        
        add_to_stack(store, 16)
        
        return int(value) if status != 0 else None
    
    def _create_session(self):
        """make a new chat session or reuse existing one"""
        if self.session_id:
            return self.session_id  # reuse existing session
        
        headers = {**self.config.BASE_HEADERS, "authorization": f"Bearer {self.token}"}
        resp = requests.post(
            f"{self.config.BASE_URL}/api/v0/chat_session/create",
            headers=headers,
            cookies=self.cookies,
            json={"agent": "chat"}
        )
        data = resp.json()
        session_id = data["data"]["biz_data"]["id"] if data.get("code") == 0 else None
        
        if session_id:
            self.session_id = session_id  # save for reuse
        
        return session_id
    
    def _get_pow_challenge(self):
        """get and solve the proof of work challenge"""
        headers = {**self.config.BASE_HEADERS, "authorization": f"Bearer {self.token}"}
        resp = requests.post(
            f"{self.config.BASE_URL}/api/v0/chat/create_pow_challenge",
            headers=headers,
            cookies=self.cookies,
            json={"target_path": "/api/v0/chat/completion"}
        )
        data = resp.json()
        if data.get("code") != 0:
            return None
        
        challenge = data["data"]["biz_data"]["challenge"]
        answer = self._compute_pow_answer(
            challenge["challenge"],
            challenge["salt"],
            challenge["difficulty"],
            challenge["expire_at"]
        )
        
        if answer is None:
            return None
        
        pow_dict = {
            "algorithm": challenge["algorithm"],
            "challenge": challenge["challenge"],
            "salt": challenge["salt"],
            "answer": answer,
            "signature": challenge["signature"],
            "target_path": challenge["target_path"],
        }
        
        return base64.b64encode(json.dumps(pow_dict).encode()).decode()
    
    def chat(self, prompt, thinking=False, search=False):
        """send a message with optional features"""
        if not self.token:
            print_status("No auth token found", "red")
            return
        
        # only create session once
        if not self.session_id:
            print_status("Creating chat session...", "cyan")
            session_id = self._create_session()
            if not session_id:
                print_status("Failed to create session", "red")
                return
        else:
            session_id = self.session_id
        
        print_status("Solving proof of work...", "cyan")
        pow_header = self._get_pow_challenge()
        if not pow_header:
            print_status("Failed to solve PoW", "red")
            return
        
        headers = {
            **self.config.BASE_HEADERS,
            "authorization": f"Bearer {self.token}",
            "x-ds-pow-response": pow_header
        }
        
        # show enabled features
        features = []
        if thinking:
            features.append("deep-think")
        if search:
            features.append("search")
        
        if features:
            print_status(f"Features: {', '.join(features)}", "cyan")
        
        print_status("Sending message...", "cyan")
        resp = requests.post(
            f"{self.config.BASE_URL}/api/v0/chat/completion",
            headers=headers,
            cookies=self.cookies,
            json={
                "chat_session_id": session_id,
                "parent_message_id": self.parent_message_id,
                "prompt": prompt,
                "ref_file_ids": [],
                "thinking_enabled": thinking,
                "search_enabled": search,
            },
            stream=True
        )
        
        if resp.status_code != 200:
            print_status(f"Request failed: {resp.status_code}", "red")
            return
        
        print_response_start()
        
        response_message_id = None
        thinking_content = ""
        main_content = ""
        
        def content_generator():
            nonlocal response_message_id, thinking_content, main_content
            for line in resp.iter_lines():
                if not line:
                    continue
                
                decoded = line.decode('utf-8', errors='ignore')
                
                if decoded.startswith("data:"):
                    data_str = decoded[5:].strip()
                    
                    if not data_str or data_str == "{}":
                        continue
                    
                    try:
                        chunk = json.loads(data_str)
                        
                        # extract response message id
                        if "response_message_id" in chunk:
                            response_message_id = chunk["response_message_id"]
                        
                        if "v" in chunk and isinstance(chunk["v"], dict):
                            if "response" in chunk["v"]:
                                resp_data = chunk["v"]["response"]
                                if "message_id" in resp_data:
                                    response_message_id = resp_data["message_id"]
                        
                        # separate thinking from main content
                        path = chunk.get("p", "")
                        
                        if "v" in chunk:
                            v_value = chunk["v"]
                            
                            # skip thinking content, only show main response
                            if "thinking" in path:
                                thinking_content += str(v_value) if isinstance(v_value, str) else ""
                                continue
                            
                            if isinstance(v_value, str) and v_value:
                                main_content += v_value
                                yield v_value
                            
                            elif isinstance(v_value, list):
                                for item in v_value:
                                    if item.get("p") == "status" and item.get("v") == "FINISHED":
                                        break
                    except:
                        pass
        
        full_content = stream_live(content_generator())
        
        # update parent message id
        if response_message_id:
            self.parent_message_id = response_message_id
        
        return full_content
    
    def upload_file(self, file_path):
        """upload a file and get its id"""
        pass  # disabled