# Blender Claude MCP Add-on

A Blender add-on that exposes a local HTTP MCP (Machine Control Protocol) server, allowing you to control Blender from external tools like Claude (Anthropic's AI assistant). The add-on provides a 3D Viewport sidebar UI for prompt input and response display, and enables real-time automation of Blender tasks via HTTP requests.

## Features
- Starts a local HTTP server inside Blender (localhost)
- Exposes endpoints for executing Python scripts, getting scene info, and more
- UI panel in the 3D Viewport sidebar for prompt/response
- Designed for integration with Claude Desktop (copy/paste workflow)

## Installation
1. Download or clone this repository.
2. In Blender, go to **Edit > Preferences > Add-ons > Install**.
3. Select the `blender_claude_addon.py` file from this folder.
4. Enable the add-on in the Add-ons list.

## Usage
### 1. Start Blender and enable the add-on
The MCP server will start automatically on `localhost:8765`.

### 2. Claude Prompt/Response Workflow
- In Blender, type your prompt in the Claude panel (3D Viewport sidebar) and copy it.
- Paste the prompt into the Claude Desktop App and get a response.
- If Claude returns Python code or JSON for the MCP server, copy it.
- Paste the code/command into the Blender panel and execute it, or use an HTTP client to POST to the MCP server.

#### Example Prompt to Claude:
```
Write Python code to make all cubes in the Blender scene 50% larger.
```

#### Example Claude Response:
```
import bpy
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.name.lower().startswith('cube'):
        obj.scale *= 1.5
```

#### How to Execute:
- Paste the code into the Blender add-on's script input and click "Run Script"
- Or POST it to `http://localhost:8765/execute_blender_script`

## Endpoints
- `POST /execute_blender_script` — Run Python code in Blender
- `GET /get_scene_info` — Get basic scene info (objects, materials, etc.)
- (More endpoints coming soon)

## Contributing
Pull requests and suggestions are welcome! Please open an issue to discuss major changes first.

## License
MIT 