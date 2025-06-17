bl_info = {
    "name": "Claude MCP Server",
    "author": "Your Name",
    "version": (0, 1),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Claude MCP",
    "description": "Expose Blender control endpoints for Claude integration.",
    "category": "3D View"
}

import bpy
import threading
import http.server
import socketserver
import json
import traceback

PORT = 8765

# --- HTTP Server ---
class MCPHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        if self.path == '/execute_blender_script':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                code = data.get('code', '')
                local_vars = {}
                exec(code, {'bpy': bpy}, local_vars)
                self._set_headers(200)
                self.wfile.write(json.dumps({'result': 'success', 'output': str(local_vars)}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'result': 'error', 'error': str(e), 'traceback': traceback.format_exc()}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_GET(self):
        if self.path == '/get_scene_info':
            try:
                scene = bpy.context.scene
                objects = [obj.name for obj in scene.objects]
                self._set_headers(200)
                self.wfile.write(json.dumps({'objects': objects}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({'result': 'error', 'error': str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

class MCPServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.httpd = socketserver.TCPServer(("localhost", PORT), MCPHandler)
    def run(self):
        self.httpd.serve_forever()
    def stop(self):
        self.httpd.shutdown()

server_thread = None

# --- Blender UI ---
class CLAUDE_PT_MCPPanel(bpy.types.Panel):
    bl_label = "Claude MCP"
    bl_idname = "CLAUDE_PT_MCPPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Claude MCP'

    def draw(self, context):
        layout = self.layout
        props = context.scene.claude_mcp_props
        layout.prop(props, "prompt")
        layout.operator("claude.copy_prompt", icon='COPYDOWN')
        layout.prop(props, "script")
        layout.operator("claude.run_script", icon='PLAY')
        layout.label(text="Response:")
        layout.prop(props, "response", text="")

class ClaudeMCPProperties(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty(name="Prompt", description="Prompt for Claude", default="")
    script: bpy.props.StringProperty(name="Script", description="Python script to run", default="", subtype='TEXT')
    response: bpy.props.StringProperty(name="Response", description="Response from Claude", default="")

class CLAUDE_OT_CopyPrompt(bpy.types.Operator):
    bl_idname = "claude.copy_prompt"
    bl_label = "Copy Prompt to Clipboard"
    def execute(self, context):
        bpy.context.window_manager.clipboard = context.scene.claude_mcp_props.prompt
        self.report({'INFO'}, "Prompt copied to clipboard.")
        return {'FINISHED'}

class CLAUDE_OT_RunScript(bpy.types.Operator):
    bl_idname = "claude.run_script"
    bl_label = "Run Script"
    def execute(self, context):
        props = context.scene.claude_mcp_props
        try:
            local_vars = {}
            exec(props.script, {'bpy': bpy}, local_vars)
            props.response = str(local_vars)
            self.report({'INFO'}, "Script executed.")
        except Exception as e:
            props.response = f"Error: {e}"
            self.report({'ERROR'}, f"Script error: {e}")
        return {'FINISHED'}

classes = [
    ClaudeMCPProperties,
    CLAUDE_PT_MCPPanel,
    CLAUDE_OT_CopyPrompt,
    CLAUDE_OT_RunScript
]

def register():
    global server_thread
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.claude_mcp_props = bpy.props.PointerProperty(type=ClaudeMCPProperties)
    if server_thread is None:
        server_thread = MCPServerThread()
        server_thread.start()

def unregister():
    global server_thread
    if server_thread is not None:
        server_thread.stop()
        server_thread = None
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.claude_mcp_props

if __name__ == "__main__":
    register() 