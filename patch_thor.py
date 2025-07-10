#!/usr/bin/env python3
# patch_thor.py - Quick fix for THOR

import sys
from pathlib import Path

# Updated chat method with proper tool handling
UPDATED_CHAT_METHOD = '''
async def chat(self, message: str, use_tools: bool = True) -> str:
    """Main chat interface"""
    try:
        self.logger.info(f"User: {message[:50]}...")
        
        # Build messages
        messages = [{"role": "user", "content": message}]
        
        # System prompt
        system_prompt = """You are THOR, an advanced AI development assistant with access to powerful tools.
        You can read/write files, run commands, analyze code, and help with software development.
        Be helpful, thorough, and always explain what you're doing.
        
        IMPORTANT: When asked to perform an action, USE THE TOOLS to actually do it, don't just describe what you would do."""
        
        # Get tools if enabled
        tools = self.get_tools_schema() if use_tools else None
        
        # Call Claude
        response = self.anthropic_client.messages.create(
            model=self.config['anthropic']['model'],
            max_tokens=self.config['anthropic']['max_tokens'],
            system=system_prompt,
            messages=messages,
            tools=tools
        )
        
        # Process response
        result_text = ""
        tool_results = []
        
        # Check if Claude wants to use tools
        for content_block in response.content:
            if content_block.type == "text":
                result_text += content_block.text
            elif content_block.type == "tool_use":
                tool_name = content_block.name
                tool_args = content_block.input
                tool_id = content_block.id
                
                self.logger.info(f"Using tool: {tool_name} with args: {tool_args}")
                
                # Execute the tool
                if tool_name in self.tools_registry:
                    try:
                        result = await self.tools_registry[tool_name](**tool_args)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": str(result)
                        })
                    except Exception as e:
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_id,
                            "content": f"Error: {str(e)}",
                            "is_error": True
                        })
                else:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": f"Unknown tool: {tool_name}",
                        "is_error": True
                    })
        
        # If tools were used, get final response
        if tool_results:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            
            final_response = self.anthropic_client.messages.create(
                model=self.config['anthropic']['model'],
                max_tokens=self.config['anthropic']['max_tokens'],
                system=system_prompt,
                messages=messages
            )
            
            result_text = final_response.content[0].text
        
        # Save to history
        self._save_conversation(message, result_text)
        
        self.logger.info("Response generated successfully")
        return result_text
        
    except Exception as e:
        self.logger.error(f"Chat error: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return f"Error: {str(e)}"
'''

# Read current file
thor_client_path = Path("src/core/thor_client.py")
content = thor_client_path.read_text()

# Find and replace the chat method
import re

# Pattern to find the chat method
pattern = r'async def chat\(self.*?\n(?=\s{0,4}[def|class|async]|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Replace the method
    new_content = content[:match.start()] + UPDATED_CHAT_METHOD.strip() + '\n' + content[match.end():]
    
    # Write back
    thor_client_path.write_text(new_content)
    print("✅ Patched THOR successfully!")
else:
    print("❌ Could not find chat method to patch")
    print("Manually update the chat method in src/core/thor_client.py")